"""
Author: Parry
Date: Jan 29, 2026

LP5811 LED Driver — Custom I2C Interface

Code adapted from Texas Instruments LP5811 reference implementation:
https://www.ti.com/product/LP5811
https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1384664/faq-lp5813-quick-program-steps-guide-for-lp5813-lp5811

---------------------------------------

This module implements I2C communication for the Texas Instruments LP5811
LED driver.

The LP5811 does NOT use a standard 7-bit I2C register addressing scheme.
Instead, it implements a CUSTOM I2C protocol with a split address format.

ADDRESSING SCHEME
-----------------
Each I2C transaction uses two address bytes composed of:

- 5-bit device (chip) address
- 9-bit register address
- 1-bit R/W flag (0 = write, 1 = read)

Address Byte 1 ( 5-bit device (chip) address + upper 2 bits of register address + R/W flag )
Address Byte 2 ( lower 7 bits of register address )

This driver manually constructs the address bytes and therefore does NOT
use standard I2C memory helpers such as `writeto_mem()` or `readfrom_mem()`.

"""
# ============================================================
# LP5811 / LP5812 I2C Slave Addresses (5-bit addresses)
# ============================================================

SLAVE_ADDRESS_BROADCAST = 0x1B
SLAVE_ADDRESS_U1        = 0x14
SLAVE_ADDRESS_U2        = 0x15
SLAVE_ADDRESS_U3        = 0x16
SLAVE_ADDRESS_U4        = 0x17


# ============================================================
# Device Configuration Registers
# ============================================================

CHIP_ENABLE_REGISTER      = 0x000
DEV_CONFIG0_REGISTER      = 0x001  # Max current & boost voltage
DEV_CONFIG1_REGISTER      = 0x002  # Drive mode & PWM frequency
DEV_CONFIG2_REGISTER      = 0x003
DEV_CONFIG3_REGISTER      = 0x004
DEV_CONFIG4_REGISTER      = 0x005
DEV_CONFIG5_REGISTER      = 0x006
DEV_CONFIG6_REGISTER      = 0x007
DEV_CONFIG7_REGISTER      = 0x008
DEV_CONFIG8_REGISTER      = 0x009
DEV_CONFIG9_REGISTER      = 0x00A
DEV_CONFIG10_REGISTER     = 0x00B
DEV_CONFIG11_REGISTER     = 0x00C
DEV_CONFIG12_REGISTER     = 0x00D


# ============================================================
# Command Registers
# ============================================================

UPDATE_CMD_REG     = 0x010
START_CMD_REG      = 0x011
STOP_CMD_REG       = 0x012
PAUSE_CMD_REG      = 0x013
CONTINUE_CMD_REG   = 0x014

# ============================================================
# LED Enable Registers
# ============================================================

LED_EN1_REG = 0x020
LED_EN2_REG = 0x021

# ============================================================
# Fault / Reset Registers
# ============================================================

FAULT_CLR_REG = 0x022
RESET_REG     = 0x023

# ============================================================
# Manual DC Registers
# ============================================================

MANUAL_DC_GAP   = 0x001
MANUAL_DC_START = 0x030

# ============================================================
# Manual PWM Registers
# ============================================================

MANUAL_PWM_GAP   = 0x001
MANUAL_PWM_START = 0x040

# ============================================================
# Auto DC Registers
# ============================================================

AUTO_DC_GAP   = 0x001
AUTO_DC_START = 0x050


# ============================================================
# Autonomous Control Registers
# ============================================================

LED_AEU_GAP = 0x01A
AEU_GAP     = 0x008

LED0_PAUSE_TIME        = 0x080
LED0_PLAYBACK_TIME     = 0x081
LED0_AEU1_PWM1         = 0x082
LED0_AEU1_PWM2         = 0x083
LED0_AEU1_PWM3         = 0x084
LED0_AEU1_PWM4         = 0x085
LED0_AEU1_PWM5         = 0x086
LED0_AEU1_SLOPE_TIME1  = 0x087
LED0_AEU1_SLOPE_TIME2  = 0x088
LED0_AEU1_PT1          = 0x089
LED0_AEU2_PWM1         = 0x08A
LED0_AEU2_PWM2         = 0x08B
LED0_AEU2_PWM3         = 0x08C
LED0_AEU2_PWM4         = 0x08D
LED0_AEU2_PWM5         = 0x08E
LED0_AEU2_SLOPE_TIME1  = 0x08F
LED0_AEU2_SLOPE_TIME2  = 0x090
LED0_AEU2_PT1          = 0x091
LED0_AEU3_PWM1         = 0x092
LED0_AEU3_PWM2         = 0x093
LED0_AEU3_PWM3         = 0x094
LED0_AEU3_PWM4         = 0x095
LED0_AEU3_PWM5         = 0x096
LED0_AEU3_SLOPE_TIME1  = 0x097
LED0_AEU3_SLOPE_TIME2  = 0x098
LED0_AEU3_PT1          = 0x099


# ============================================================
# Status / Flag Registers
# ============================================================

TSD_CONFIG_STATUS = 0x300
LOD_STATUS1       = 0x301
LOD_STATUS2       = 0x302
LSD_STATUS1       = 0x303
LSD_STATUS2       = 0x304


# ============================================================
# Test Registers
# ============================================================

OTP_CONFIG_REGISTER      = 0x352
SRAM_CONFIG_REGISTER     = 0x353
CLOCK_GATING_EN_REGISTER = 0x354


# ============================================================
# Register Values
# ============================================================

CHIP_DISABLE = 0x00
CHIP_ENABLE  = 0x01

LOD_CLEAR_EN = 0x01
LSD_CLEAR_EN = 0x02
RESET_EN     = 0x66


# ============================================================
# LED Index Values
# ============================================================

LED0  = 0x00
LED1  = 0x01
LED2  = 0x02
LED3  = 0x03
LED_A0 = 0x04
LED_A1 = 0x05
LED_A2 = 0x06
LED_B0 = 0x07
LED_B1 = 0x08
LED_B2 = 0x09
LED_C0 = 0x0A
LED_C1 = 0x0B
LED_C2 = 0x0C
LED_D0 = 0x0D
LED_D1 = 0x0E
LED_D2 = 0x0F

LED_A = LED0 #white
LED_B = LED1 #blue
LED_C = LED2 #green 
LED_D = LED3 #red


# ============================================================
# Command Values
# ============================================================

UPDATE_CMD_VALUE   = 0x55
START_CMD_VALUE    = 0xFF
STOP_CMD_VALUE     = 0xAA
PAUSE_CMD_VALUE    = 0x33
CONTINUE_CMD_VALUE = 0xCC 


# ============================================================
# Autonomous Execution Units
# ============================================================

AEU1 = 0x00
AEU2 = 0x01
AEU3 = 0x02

from machine import I2C
import time
class LP5811:
    def __init__(self, i2c: I2C, chip_addr: int = 0b11011):
        """
        chip_addr: 5-bit LP5811 device address (A4..A0)
                   Examples:
                     0x14 → U1
                     0x15 → U2
                     0x16 → U3
                     0x17 → U4
                     0x1B → Broadcast
        """
        self.i2c = i2c
        self.chip_addr = chip_addr & 0x1F  # enforce 5-bit address
        self._current_rgb = [0, 0, 0,0]  # Track current RGBW    values for fades
    # ------------------------------------------------------------------
    # Address construction
    # ------------------------------------------------------------------

    def _build_addr7(self, reg: int) -> int:
        """
        Build 7-bit I2C address for LP5811.

        Format (7-bit):
        [101][A4 A3][R9 R8]

        R/W bit is handled automatically by MicroPython.
        """
        r9_r8 = (reg >> 8) & 0x03
        return (self.chip_addr << 2) | r9_r8

    # ------------------------------------------------------------------
    # Register access
    # ------------------------------------------------------------------

    def write_reg(self, reg: int, value: int):
        """
        Write one byte to a 10-bit register.
        """
        addr7 = self._build_addr7(reg)
        reg_lsb = reg & 0xFF

        self.i2c.writeto(
            addr7,
            bytes([reg_lsb, value & 0xFF])
        )

    def read_reg(self, reg: int) -> int:
        """
        Read one byte from a 10-bit LP5811 register.
        Compatible with all MicroPython ports.
        """
        addr7 = self._build_addr7(reg)
        reg_lsb = reg & 0xFF

        # Write register pointer (no stop if supported)
        self.i2c.writeto(addr7, bytes([reg_lsb]), False)

        # Read one byte
        data = self.i2c.readfrom(addr7, 1)

        return data[0]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        # Check if the LP5811 ACKs by reading a known register.
        try:
            _ = self.read_reg(0x000)  # Chip Enable register
            return True
        except OSError:
            return False
        
    #initialization sequence for manual mode
    def init_manual(self):
        self.write_reg(CHIP_ENABLE_REGISTER, 0x01)   # Chip_Enable_Register
        self.write_reg(DEV_CONFIG0_REGISTER, 0x00)   # Dev_Config0_Register current limit 25mA
        
        # lsd_threshold = 0.65Vcc, shut off if cathode voltage surpasses set amount. Also enabled short and open fault
        self.write_reg(DEV_CONFIG12_REGISTER, 0x0F)   
        self.write_reg(UPDATE_CMD_REG, UPDATE_CMD_VALUE)   # Update LED params

        #Check config error status. See if any fault had been tripped
        status = self.read_reg(TSD_CONFIG_STATUS)  # TSD_CONFIG_STATUS
        if status != 0x00:
            raise RuntimeError("LP5811 config error: status=0x%02X" % status)

        # Enable all LEDs
        self.write_reg(LED_EN1_REG, 0x0F)

        # Set peak current for LEDs
        peak_current = 0xFF
        for reg in range(MANUAL_DC_START , MANUAL_DC_START + 4):
            self.write_reg(reg, peak_current)

        # Set PWM duty cycle for all LEDs
        pwm_duty = 0x10
        for reg in range(MANUAL_PWM_START, MANUAL_PWM_START + 4):
            self.write_reg(reg, pwm_duty)

        return True

    def fade_leds_manual(self, target_rgb: list, duration_ms: int, steps: int = 64):
        """
        Fade LEDs from current RGB to target RGB using manual PWM.

        target_rgb  : [R, G, B] target values (0–255)
        duration_ms : total fade time in milliseconds
        steps       : number of fade steps
        """

        start_register = MANUAL_PWM_START
        delay_ms = duration_ms // steps

        start_rgb = self._current_rgb.copy()

        for step in range(steps + 1):
            for i in range(4):
                value = start_rgb[i] + (target_rgb[i] - start_rgb[i]) * step // steps
                self.write_reg(start_register + i, value)

            time.sleep_ms(delay_ms)

        # Save state
        self._current_rgb = target_rgb.copy()



# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------

if __name__ == "__main__":
    i2c = I2C(
        0,
        scl=Pin(22),
        sda=Pin(21),
        freq=100_000
    )

    lp = LP5811(i2c)

    if lp.ping():
        print("LP5811 detected!")

        # Example writes (replace with real init sequence)
        lp.write_reg(0x000, 0x01)  # Chip Enable
        time.sleep(0.1)

        lp.write_reg(0x020, 0xFF)  # Enable LEDs (example)
        time.sleep(1)

        lp.write_reg(0x020, 0x00)  # Disable LEDs
    else:
        print("LP5811 not detected.")