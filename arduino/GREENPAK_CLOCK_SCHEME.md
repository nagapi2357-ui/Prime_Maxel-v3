# SLG47004V Clock Scheme for CNT/DLY — Reference

## From Datasheet Section 16.5 (Page 150-151)

Each CNT/DLY has a **4-bit clock source selector** (16 options):

| Selector | Clock Source |
|----------|-------------|
| 0 | OSC0 (2.048 kHz pre-divided) |
| 1 | OSC0 / 8 |
| 2 | OSC0 / 64 |
| 3 | OSC0 / 512 |
| 4 | OSC0 / 4096 |
| 5 | OSC0 / 32768 |
| 6 | OSC0 / 262144 |
| 7 | OSC1 (2.048 MHz pre-divided) |
| 8 | OSC1 / 8 (256 kHz) |
| 9 | OSC1 / 64 (32 kHz) |
| 10 | OSC1 / 512 (4 kHz) |
| 11 | OSC2 (25 MHz pre-divided) |
| 12 | OSC2 / 4 (6.25 MHz) |
| 13 | CNT(x-1) overflow (cascade from previous counter) |
| 14 | Connection Matrix Output (external, per CNT) |
| 15 | None (disabled) |

## Key Insight: Counter Output Frequency

In **counter mode** with toggle output:
```
f_out = f_clk / (2 × (counter_data + 1))
```

But from Section 8.3.2, counter mode generates a pulse of width = counter_data × clock periods,
then resets. The output is HIGH for counter_data clocks, then toggles.

Actually, in **one-shot mode** or **counter mode**, the behavior differs.
For a **free-running square wave**, we want the counter to count up to counter_data, 
toggle output, and repeat. This is the standard counter toggle mode.

## Revised Frequency Calculations

### Using OSC1 directly (2.048 MHz, selector 7):
f_out = 2,048,000 / (2 × (N + 1))

For 1024 Hz: N = 2,048,000 / (2 × 1024) - 1 = 999
For 341.3 Hz: N = 2,048,000 / (2 × 341.33) - 1 = 2999
For 204.8 Hz: N = 2,048,000 / (2 × 204.8) - 1 = 4999
For 146.3 Hz: N = 2,048,000 / (2 × 146.286) - 1 = 6999
For 93.1 Hz: N = 2,048,000 / (2 × 93.091) - 1 = 10999
For 78.8 Hz: N = 2,048,000 / (2 × 78.769) - 1 = 12999

CNT6 is 16-bit: max N = 65535. All our values fit!
CNT0-CNT5 are 8-bit: max N = 255. Our values DON'T fit for 8-bit counters!

### IMPORTANT: Only CNT6 (the 16-bit counter in MF6) can handle our divisors!
The 8-bit counters (CNT0-5) max at 255, but we need up to 12999.

### Alternative: Use OSC0 (2.048 kHz) with 8-bit counters
f_out = 2048 / (2 × (N + 1))

For a base of ~128 Hz: N = 2048/(2×128) - 1 = 7
But we can't get exact prime ratios because 2048/(2×(N+1)) has limited resolution.

### Alternative: Use OSC1/512 = 4 kHz with 8-bit counters
f_out = 4000 / (2 × (N + 1))

For ~30 Hz base: N values 0-255 give 7.8 Hz to 2000 Hz
Still hard to get exact prime ratios.

## Problem: Only ONE 16-bit counter per chip!

Each SLG47004V has only one 16-bit counter (CNT6 in MF6).
But each chip only needs ONE frequency — one counter per cell!
So CNT6 in each chip generates that chip's prime-ratio frequency. ✅

## Go Configure Steps

In Go Configure, to set up MF6 as a counter:
1. Set MF6 "Multi-function mode" to "CNT/DLY" 
2. **Click on the CNT/DLY sub-block** (not the LUT sub-block) in the canvas
3. In properties, set:
   - Clock source: OSC1 (2.048 MHz)  — selector 7
   - Mode: Counter (free-running toggle)
   - Counter data: 999 (for 1024 Hz cell)
   - Edge: Rising
   - Output polarity: Non-inverted

4. Route the CNT6 output through the connection matrix to OA0 or a GPIO

## Connecting CNT6 Output to OA0_OUT (Pin 5)

The OA0 is an analog op-amp. We can't directly drive a digital counter output 
through an analog op-amp in the usual sense. 

**Better approach:** Route CNT6 output to a **GPIO pin** and use that as the 
signal output. In the v3 board schematic, we need to check if any GPIO is 
connected (most are NC). If not, we may need to use OA0 differently — 
perhaps as a buffer/follower for the counter output via the internal connection matrix.

Or: Use OA0 in **comparator mode** with the counter output driving enable/disable,
creating a shaped waveform.

**Simplest test:** Route CNT6 output → GPIO0 (pin 12) or another connected IO pin,
and probe it directly. This validates the oscillator before involving OA0.
