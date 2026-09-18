"""Cheap Fiber Analyzer - Serial Client."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from database import (
    init_db,
    insert_event,
    insert_measurement,
    update_system_state,
)

FIELD_RE = re.compile(
    r"(ADC12|ADC13|DAC1|DAC2)\s*=\s*(-?\d+)",
    re.IGNORECASE,
)


def parse_line(line: str) -> dict[str, int] | None:
    values: dict[str, int] = {}

    for name, raw_value in FIELD_RE.findall(line):
        values[name.upper()] = int(raw_value)

    required = {"ADC12", "ADC13", "DAC1", "DAC2"}
    if not required.issubset(values):
        return None

    for key in required:
        if not 0 <= values[key] <= 4095:
            raise ValueError(f"{key} must be between 0 and 4095")

    return values


def process_line(
    line: str,
    source: str = "STM32",
    detail: str = "Live measurement from STM32",
) -> bool:
    values = parse_line(line)
    if values is None:
        return False

    insert_measurement(
        adc12=values["ADC12"],
        adc13=values["ADC13"],
        dac1=values["DAC1"],
        dac2=values["DAC2"],
        source=source,
    )

    update_system_state(
        connection="CONNECTED",
        adc_status="OK",
        dac_status="OK",
        serial_status="RX",
    )

    insert_event(
        event_type="MEASUREMENT_RX",
        value=f"ADC12={values['ADC12']}, ADC13={values['ADC13']}",
        detail=detail,
    )

    return True


def run_stdin() -> None:
    print("CHEAP FIBER ANALYZER - TEST SERIAL")
    print("Nhap frame hoac Ctrl+C de thoat.")

    update_system_state(
        connection="CONNECTED",
        adc_status="WAITING",
        dac_status="WAITING",
        serial_status="STDIN TEST",
    )

    while True:
        line = input("> ").strip()
        if not line:
            continue

        try:
            success = process_line(
                line,
                source="TEST",
                detail="Temporary TEST protocol",
            )
            print("OK - Saved to SQLite" if success else "ERROR - Invalid TEST frame")
        except ValueError as exc:
            print(f"ERROR - Invalid value: {exc}")
            insert_event("TEST_ERROR", line, str(exc))


def run_serial(port: str, baudrate: int) -> None:
    try:
        import serial
    except ImportError:
        print("pyserial chua duoc cai. Chay: py -m pip install pyserial")
        return

    print(f"Opening {port} @ {baudrate}")
    update_system_state("CONNECTING", "WAITING", "WAITING", f"OPEN {port}")

    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=1) as ser:
            update_system_state("CONNECTED", "WAITING", "WAITING", "RX")
            print("Serial connected.")

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                print("RX:", line)
                try:
                    success = process_line(line, source="STM32", detail="Live measurement from STM32")
                    print("OK - Saved to SQLite" if success else "Ignored - invalid STM32 frame")
                except ValueError as exc:
                    print("RX ERROR:", exc)
                    insert_event("RX_ERROR", line, str(exc))

    except Exception as exc:
        print("Serial connection error:", exc)
        update_system_state("DISCONNECTED", "UNKNOWN", "UNKNOWN", "ERROR")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cheap Fiber Analyzer Serial Client")
    parser.add_argument("--serial", help="COM port, example COM4")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--stdin", action="store_true", help="Run TEST mode using keyboard input")
    args = parser.parse_args()

    init_db()
    if args.stdin or not args.serial:
        run_stdin()
    else:
        run_serial(args.serial, args.baud)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
