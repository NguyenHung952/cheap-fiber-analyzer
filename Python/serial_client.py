"""
Cheap Fiber Analyzer - Serial Client

TEST protocol hiện tại:

ADC12=2048;ADC13=1024;DAC1=2000;DAC2=1000

Lưu ý:
Đây chỉ là protocol TEST để kiểm tra:

TEST INPUT
    ↓
Python
    ↓
SQLite
    ↓
Flask
    ↓
Web

Chưa phải protocol RS485 chính thức của STM32.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# ============================================================
# PATH
# ============================================================

PYTHON_DIR = Path(__file__).resolve().parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


# ============================================================
# DATABASE
# ============================================================

from database import (
    init_db,
    insert_event,
    insert_measurement,
    update_system_state,
)


# ============================================================
# TEST FRAME FORMAT
# ============================================================

FIELD_RE = re.compile(
    r"(ADC12|ADC13|DAC1|DAC2)\s*=\s*(-?\d+)",
    re.IGNORECASE,
)


# ============================================================
# PARSE TEST FRAME
# ============================================================

def parse_test_line(line: str) -> dict[str, int] | None:
    """
    Parse:

    ADC12=2048;ADC13=1024;DAC1=2000;DAC2=1000
    """

    values: dict[str, int] = {}

    matches = FIELD_RE.findall(line)

    for name, raw_value in matches:
        values[name.upper()] = int(raw_value)

    required = {
        "ADC12",
        "ADC13",
        "DAC1",
        "DAC2",
    }

    if not required.issubset(values):
        return None

    # ADC 12-bit
    for key in ("ADC12", "ADC13"):
        value = values[key]

        if not 0 <= value <= 4095:
            raise ValueError(
                f"{key} must be between 0 and 4095"
            )

    # DAC 12-bit
    for key in ("DAC1", "DAC2"):
        value = values[key]

        if not 0 <= value <= 4095:
            raise ValueError(
                f"{key} must be between 0 and 4095"
            )

    return values


# ============================================================
# SAVE FRAME
# ============================================================

def process_line(line: str) -> bool:
    values = parse_test_line(line)

    if values is None:
        return False

    # --------------------------------------------------------
    # Save measurement
    # --------------------------------------------------------

    insert_measurement(
        adc12=values["ADC12"],
        adc13=values["ADC13"],
        dac1=values["DAC1"],
        dac2=values["DAC2"],
        source="TEST",
    )

    # --------------------------------------------------------
    # Update system status
    # --------------------------------------------------------

    update_system_state(
        connection="CONNECTED",
        adc_status="OK",
        dac_status="OK",
        serial_status="RX",
    )

    # --------------------------------------------------------
    # Save event
    # --------------------------------------------------------

    insert_event(
        event_type="MEASUREMENT_RX",
        value=(
            f"ADC12={values['ADC12']}, "
            f"ADC13={values['ADC13']}"
        ),
        detail="Temporary TEST protocol",
    )

    return True


# ============================================================
# STDIN TEST MODE
# ============================================================

def run_stdin() -> None:

    print()
    print("==========================================")
    print(" CHEAP FIBER ANALYZER - TEST SERIAL")
    print("==========================================")
    print()
    print("Nhap frame:")
    print(
        "ADC12=2048;ADC13=1024;"
        "DAC1=2000;DAC2=1000"
    )
    print()
    print("Ctrl+C de thoat.")
    print()

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

            success = process_line(line)

            if success:
                print("OK - Saved to SQLite")

            else:
                print("ERROR - Invalid TEST frame")

        except ValueError as exc:

            print(
                f"ERROR - Invalid value: {exc}"
            )

            insert_event(
                event_type="TEST_ERROR",
                value=line,
                detail=str(exc),
            )


# ============================================================
# REAL SERIAL MODE
# ============================================================

def run_serial(
    port: str,
    baudrate: int,
) -> None:

    try:
        import serial

    except ImportError:

        print(
            "pyserial chưa được cài."
        )

        print(
            "Chạy:"
        )

        print(
            "py -m pip install pyserial"
        )

        return

    print()
    print(
        f"Opening {port} @ {baudrate}"
    )

    update_system_state(
        connection="CONNECTING",
        adc_status="WAITING",
        dac_status="WAITING",
        serial_status=f"OPEN {port}",
    )

    try:

        with serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1,
        ) as ser:

            update_system_state(
                connection="CONNECTED",
                adc_status="WAITING",
                dac_status="WAITING",
                serial_status="RX",
            )

            print(
                "Serial connected."
            )

            while True:

                raw = ser.readline()

                if not raw:
                    continue

                line = raw.decode(
                    "utf-8",
                    errors="replace",
                ).strip()

                if not line:
                    continue

                print(
                    "RX:",
                    line,
                )

                try:

                    success = process_line(line)

                    if success:

                        print(
                            "OK - Saved to SQLite"
                        )

                    else:

                        print(
                            "Ignored - "
                            "invalid TEST frame"
                        )

                except ValueError as exc:

                    print(
                        "RX ERROR:",
                        exc,
                    )

                    insert_event(
                        event_type="RX_ERROR",
                        value=line,
                        detail=str(exc),
                    )

    except Exception as exc:

        print(
            "Serial connection error:",
            exc,
        )

        update_system_state(
            connection="DISCONNECTED",
            adc_status="UNKNOWN",
            dac_status="UNKNOWN",
            serial_status="ERROR",
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Cheap Fiber Analyzer Serial Client"
    )

    parser.add_argument(
        "--serial",
        help="COM port, example COM5",
    )

    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Baudrate",
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Run TEST mode using keyboard input",
    )

    args = parser.parse_args()

    # Create DB/tables if needed
    init_db()

    # --------------------------------------------------------
    # TEST MODE
    # --------------------------------------------------------

    if args.stdin or not args.serial:

        run_stdin()
        return

    # --------------------------------------------------------
    # REAL SERIAL MODE
    # --------------------------------------------------------

    run_serial(
        port=args.serial,
        baudrate=args.baud,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print()
        print("Stopped.")