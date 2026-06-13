#!/usr/bin/env python3
"""T1/T2/T3 signal scanner for candidate pool stocks.
Reads candidate_pool from research.db, pulls OHLCV via akshare (Sina),
checks Stage-2 breakout conditions, writes trigger_signal table."""

import sqlite3
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB = '/home/admin/.hermes/data/research.db'

def get_pool_stocks():
    """Get active candidate pool stocks from DB"""
    db = sqlite3.connect(DB)
    rows = db.execute(
        "SELECT ts_code, enter_gate_score FROM candidate_pool WHERE status='active'"
    ).fetchall()
    db.close()
    return rows

def pull_ohlcv(ts_code):
    """Pull daily OHLCV via akshare Sina source, return DataFrame"""
    code = ts_code.split('.')[0]
    exchange = 'sh' if ts_code.endswith('.SH') else 'sz'
    symbol = f'{exchange}{code}'
    try:
        df = ak.stock_zh_a_daily(
            symbol=symbol,
            start_date='20250101',
            end_date=datetime.now().strftime('%Y%m%d'),
            adjust='qfq'
        )
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  ❌ {ts_code}: {e}")
        return None

def check_t1_trend(df):
    """T1: close > MA50 > MA150 > MA200, MA200 slope positive (21d)"""
    df = df.copy()
    df['MA50'] = df['close'].rolling(50).mean()
    df['MA150'] = df['close'].rolling(150).mean()
    df['MA200'] = df['close'].rolling(200).mean()
    
    last = df.iloc[-1]
    # Need at least 200 bars
    if pd.isna(last['MA200']):
        return False, 0.0, 0.0, 0.0, 0.0
    
    close = last['close']
    ma50 = last['MA50']
    ma150 = last['MA150']
    ma200 = last['MA200']
    
    # Slope: MA200 today > MA200 21 days ago
    if len(df) >= 221:
        ma200_21d_ago = df.iloc[-22]['MA200']
        slope_up = ma200 > ma200_21d_ago
    else:
        slope_up = True  # insufficient history, be lenient
    
    passed = (close > ma50 > ma150 > ma200) and slope_up
    return passed, close, ma50, ma150, ma200

def check_t2_breakout(df, min_vol_mult=1.5, dist_52w_pct=5.0):
    """T2: close >= 52w high * 0.95, volume >= MA50(vol) * 1.5"""
    df = df.copy()
    df['vol_ma50'] = df['volume'].rolling(50).mean()
    
    high_52w = df['close'].rolling(250).max().iloc[-1]
    if pd.isna(high_52w):
        return False, 0, 0, 0, 0
    
    last = df.iloc[-1]
    close = last['close']
    vol = last['volume']
    vol_ma50 = last['vol_ma50']
    
    dist_pct = (high_52w - close) / high_52w * 100
    vol_ratio = vol / vol_ma50 if vol_ma50 > 0 else 0
    
    passed = (dist_pct <= dist_52w_pct) and (vol_ratio >= min_vol_mult)
    return passed, dist_pct, vol_ratio, high_52w, vol_ma50

def check_t3_base(df, min_bars=30, max_amplitude=0.25):
    """T3: consolidation base >= 30 bars, amplitude < 25%"""
    close = df['close'].values
    n = len(close)
    
    # Find recent consolidation: look for a period of sideways movement
    # ending near the current price
    best_bars = 0
    base_low = close[-1]
    
    # Scan backwards for consolidation periods
    for end in range(n-1, n-30, -1):
        for start in range(end-30, max(0, end-120), -1):
            segment = close[start:end+1]
            seg_high = np.max(segment)
            seg_low = np.min(segment)
            amplitude = (seg_high - seg_low) / seg_low if seg_low > 0 else float('inf')
            bars = end - start + 1
            
            if amplitude <= max_amplitude and bars >= min_bars and bars > best_bars:
                best_bars = bars
                base_low = seg_low
    
    passed = best_bars >= min_bars
    return passed, best_bars, base_low

def scan_stock(ts_code, df):
    """Run T1/T2/T3 on a single stock"""
    if df is None or len(df) < 50:
        return None
    
    t1, close, ma50, ma150, ma200 = check_t1_trend(df)
    t2, dist_pct, vol_ratio, high_52w, vol_ma = check_t2_breakout(df)
    t3, base_bars, base_low = check_t3_base(df)
    
    last_date = df['date'].iloc[-1].strftime('%Y-%m-%d')
    
    return {
        'ts_code': ts_code,
        'date': last_date,
        'close': round(close, 2),
        't1': t1, 't2': t2, 't3': t3,
        'trigger': t1 and t2 and t3,
        'ma50': round(ma50, 2) if ma50 else None,
        'ma150': round(ma150, 2) if ma150 else None,
        'ma200': round(ma200, 2) if ma200 else None,
        'dist_52w_pct': round(dist_pct, 2),
        'vol_ratio': round(vol_ratio, 2),
        'base_weeks': round(base_bars / 5, 1) if base_bars else 0,
        'base_low': round(base_low, 2) if base_low else None,
    }

def write_signals(results):
    """Write scan results to trigger_signal table"""
    db = sqlite3.connect(DB)
    today = datetime.now().strftime('%Y-%m-%d')
    
    for r in results:
        if r is None:
            continue
        db.execute('''
            INSERT INTO trigger_signal 
            (ts_code, signal_date, t1_pass, t2_pass, t3_pass,
             close, vol_ratio, dist_52w_high, base_weeks, base_low)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            r['ts_code'], r['date'],
            1 if r['t1'] else 0, 1 if r['t2'] else 0, 1 if r['t3'] else 0,
            r['close'], r['vol_ratio'], r['dist_52w_pct'],
            r['base_weeks'], r['base_low']
        ))
    
    db.commit()
    
    # Also update pool stocks' latest signal status (optional, for dashboard)
    db.close()

def main():
    stocks = get_pool_stocks()
    print(f"📊 扫描 {len(stocks)} 只候选池标的\n")
    
    results = []
    for ts_code, gate_score in stocks:
        name = ts_code
        print(f"  {ts_code} (Gate={gate_score}) ...", end=' ')
        df = pull_ohlcv(ts_code)
        if df is None or len(df) < 50:
            print("数据不足")
            continue
        
        r = scan_stock(ts_code, df)
        results.append(r)
        
        status = "🔥 TRIGGER!" if r['trigger'] else (
            f"T1={'✓' if r['t1'] else '✗'} T2={'✓' if r['t2'] else '✗'} T3={'✓' if r['t3'] else '✗'}"
        )
        print(status)
        if r['trigger']:
            print(f"     Close={r['close']} MA50={r['ma50']} MA150={r['ma150']} MA200={r['ma200']}")
            print(f"     52w高距={r['dist_52w_pct']}% 量比={r['vol_ratio']}x 基底={r['base_weeks']}周")
    
    if results:
        write_signals(results)
        print(f"\n✅ 已写入 {len(results)} 条信号到 trigger_signal")
    
    # Summary
    triggers = [r for r in results if r and r['trigger']]
    if triggers:
        print(f"\n🚨 {len(triggers)} 只标的触发 Stage-2 突破！")
        for t in triggers:
            print(f"   {t['ts_code']} @ {t['close']}")
    else:
        print(f"\n📭 本期无触发信号")

if __name__ == '__main__':
    main()
