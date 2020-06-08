# IV_instrument_rack
Program to interface with instrument rack for superconductor characterization


Welcome to the IV_instrument_rack wiki!

# Introduction

This repository contains scripts and routines for communicating with various equipment relevant for superconducting magnet operation. It is updated as time goes on, and is full of bugs - please use this as motivation for your own projects, do not try to control your own instruments and power supplies with the contents herein.

# Usage and Scope

A Picoscope 4824 is assumed to be connected to the control computer by a USB3 interface. The Picoscope can be operated either in streaming mode (i.e. for logging acoustic sensors over long magnet ramps), or in (rapid) block mode for short measurements of very high sampling frequency.

All other instruments are routed through an Agilent E5810B hub, and the work here relies heavily on the "Pyvisa" and "pyvisa-py" modules. This E5810B hub connects to a control computer via ethernet, and GPIB, RS-232 and USB instruments can be connected into the E5810B. As a result, you establish a new connection to a new GPIB instrument as:

 "my_inst = rm.open_resource("TCPIP::169.254.58.10::gpib0,22::INSTR")" 

where 169.254.58.10 is the gateway to the E5810B hub (you will have to modify for your application), and "gpib0,22" is the GPIB number (22) that was programmed in the instrument.


# Programmed Instruments

- Agilent 34420A Nanovolt meter

- Keithley 2010 multimeter

- Agilent 33210A function generator

- Sorenson SGA 10/1200 Power supply (DO NOT RUN YOUR OWN POWER SUPPLY WITH ANY CODE IN THIS REPOSITORY. USE AT YOUR OWN RISK.)

- Picoscope 4824

# Programmed Routines

NONE OF THE PROGRAMMED ROUTINES HAVE BEEN TESTED

- IV curve using Sorensen power supply, nanovolt meter across sample and multimeter as shunt

- Curve fit a power law to the measured IV curve

- Monitor the sample voltage during cooldown

- Basic functionality for initiating power supply ramps


