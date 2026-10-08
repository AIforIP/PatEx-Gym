## Metadata

- Application Number: 17448879
- Title: Touch sensing with water rejection
- Filing Date: 2021-09-25
- Dataset Category: G

## Inventors / Authors

- Andrew William Shorten
- Sai Zhang
- Andreas Johannes Koeberl
- Eric S. Winokur
- Liqun Yang
- II Sabino Joseph PIETRANGELO
- Branislav JOVANOVIC
- Ari Y. BENBASAT

## Classification

- Main CPC: G06F3/04186
- Main IPC: Not available

## Abstract

Techniques for rejecting apparent (but false) touches caused by objects such as water droplets located in areas with parasitic capacitive paths to ground are disclosed. To minimize these false touches, one or more guard conductors can be located in proximity to the housing and driven with a stimulation signal to shield objects from being capacitively coupled to ground through the housing. In some examples images of touch can be obtained from a non-bootstrapped or bootstrapped scan and also an extended bootstrapped scan wherein the guard conductor is driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples, the results of the extended bootstrapped scan can be subtracted from the non-bootstrapped or bootstrapped scan to identify and reject apparent touches resulting from capacitive coupling to ground.

## Initial Submission Claims

AMENDMENTS TO THE CLAIMS

1\. (Original) An electronic device comprising:
a housing;
a cover substrate;
a touch sensor panel comprising a plurality of touch nodes that are configured to be driven with a first stimulation signal; and
one or more conductors disposed between the cover substrate and the housing and electrically insulated from the housing, wherein the one or more conductors are configured to be biased at a first potential in a first mode of touch operation and driven with a second stimulation signal in a second mode of touch operation.

2\. (Original) The electronic device of claim 1, wherein the second stimulation signal has a same frequency, a same phase, and a same amplitude as the first stimulation signal.

3\. (Original) The electronic device of claim 1, wherein at least a portion of the one or more conductors is disposed at an edge of the cover substrate.

4\. (Original) The electronic device of claim 1, further comprising:
one or more gaskets between the cover substrate and the housing;
wherein the one or more conductors are formed in the one or more gaskets.

5\. (Original) The electronic device of claim 1, further comprising:
sensing circuitry configured to sense the plurality of touch nodes driven with the first stimulation signal.

6\. (New) The electronic device of claim 1, further comprising:
processing circuitry configured to:
perform a first scan in the first mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with a first stimulation signal in one or more scan steps, the first scan including first touch signals grouped into first patches indicative of objects capacitively coupled to ground; and
perform a second scan in the second mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with the first stimulation signal while shielding against capacitive coupling paths to ground through the housing, the second scan including second touch signals grouped into second patches indicative of objects capacitively coupled to ground through one or more objects contacting the cover substrate of the electronic device.

7\. (New) The electronic device of claim 6, wherein the processing circuitry is further configured to:
determine which of the first patches are indicative of objects capacitively coupled to ground through the electronic device using results of the first scan and results of the second scan; and
exclude the first patches indicative of objects capacitively coupled to ground through the electronic device from further touch processing.

8\. (New) The electronic device of claim 6, wherein the processing circuitry is further configured to:
determine which of the first patches are indicative of objects capacitively coupled to ground through the one or more objects using results of the first scan and results of the second scan; and
further processing the first patches indicative of objects capacitively coupled to ground through the one or more objects.

9\. (New) The electronic device of claim 1, the touch sensing device of claim 1, wherein the plurality of touch nodes and the one or more conductors are formed in a same layer.

10\. (New) The electronic device of claim 1, the touch sensing device of claim 1, wherein the plurality of touch nodes and the one or more conductors are formed on opposite sides of the cover substrate.

11\. (New) The electronic device of claim 1, wherein a first conductor of the one or more conductors wraps around from a first surface of the cover substrate to a second surface of the cover substrate.

12\. (New) The electronic device of claim 1, wherein the plurality of touch nodes form an active touch area for the touch sensor panel and the cover substrate, and the one or more conductors are located at least partially outside the active touch area wherein the one or more conductors are an extension of one or more driven shield layers in proximity to the active touch area, the one or more conductors extending the one or more shield layers beyond the active touch area.

13\. (New) A method comprising:
at an electronic device comprising a housing, a cover substrate, a touch sensor panel comprising a plurality of touch nodes that are configured to be driven with a first stimulation signal, and one or more conductors disposed between the cover substrate and the housing and electrically insulated from the housing:
biasing the one or more conductors at a first potential in a first mode of touch operation; and
driving the one or more conductors with a second stimulation signal in a second mode of touch operation to shield one or more objects contacting the cover substrate from capacitively coupling to ground through the housing.

14\. (New) The method of claim 13, wherein the second stimulation signal has a same frequency, a same phase, and a same amplitude as the first stimulation signal.

15\. (New) The method of claim 13, further comprising:
performing a first scan in the first mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with a first stimulation signal in one or more scan steps, the first scan including first touch signals grouped into first patches indicative of objects capacitively coupled to ground; and performing a second scan in the second mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with the first stimulation signal while shielding against capacitive coupling paths to ground through the housing, the second scan including second touch signals grouped into second patches indicative of objects capacitively coupled to ground through the one or more objects.

16\. (New) The method of claim 15, further comprising:
determining which of the first patches are indicative of objects capacitively coupled to ground through the electronic device using results of the first scan and results of the second scan;
and excluding the first patches indicative of objects capacitively coupled to ground through the electronic device from further touch processing.

17\. (New) A non-transitory computer readable storage medium storing instructions that when executed by an electronic device comprising a housing, a cover substrate, a touch sensor panel comprising a plurality of touch nodes that are configured to be driven with a first stimulation signal, and one or more conductors disposed between the cover substrate and the housing and electrically insulated from the housing, cause the electronic device to:
bias the one or more conductors at a first potential in a first mode of touch operation; and
drive the one or more conductors with a second stimulation signal in a second mode of touch operation to shield one or more objects contacting the cover substrate from capacitively coupling to ground through the housing.

18\. (New) The non-transitory computer readable storage medium of claim 17, wherein the second stimulation signal has a same frequency, a same phase, and a same amplitude as the first stimulation signal.

19\. (New) The non-transitory computer readable storage medium of claim 17, the instructions, when executed by the electronic device, further cause the electronic device to: perform a first scan in the first mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with a first stimulation signal in one or more scan steps, the first scan including first touch signals grouped into first patches indicative of objects capacitively coupled to ground; and
perform a second scan in the second mode of touch operation by driving the plurality of touch nodes of the touch sensor panel with the first stimulation signal while shielding against capacitive coupling paths to ground through the housing, the second scan including second touch signals grouped into second patches indicative of objects capacitively coupled to ground through the one or more objects.

20\. (New) The non-transitory computer readable storage medium of claim 19, the instructions, when executed by the electronic device, further cause the electronic device to:
determine which of the first patches are indicative of objects capacitively coupled to ground through the electronic device using results of the first scan and results of the second scan; and
exclude the first patches indicative of objects capacitively coupled to ground through the electronic device from further touch processing.
2 3 4 5 6 4858-8703-9744, v. 1

## Description

CROSS-REFERENCE TO RELATED APPLICATIONS
This application is a continuation of U.S. patent application Ser. No. 16/786,921, filed Feb. 10, 2020, which claims benefit of U.S. Provisional Application No. 62/897,118, filed Sep. 6, 2019, the contents of which are hereby incorporated by reference in their entirety for all purposes.
FIELD OF THE DISCLOSURE
This relates generally to touch sensor panels, and more particularly to techniques for rejecting water droplets located near the edges of the touch sensor panels.
BACKGROUND OF THE DISCLOSURE
Many types of input devices are presently available for performing operations in a computing system, such as buttons or keys, mice, trackballs, joysticks, touch sensor panels, touch screens and the like. Touch screens, in particular, are popular because of their ease and versatility of operation as well as their declining price. Touch screens can include a touch sensor panel, which can be a clear panel with a touch-sensitive surface, and a display device such as a liquid crystal display (LCD), light emitting diode (LED) display or organic light emitting diode (OLED) display that can be positioned partially or fully behind the panel so that the touch-sensitive surface can cover at least a portion of the viewable area of the display device. Touch screens can allow a user to perform various functions by touching the touch sensor panel using a finger, stylus or other object at a location often dictated by a user interface (UI) being displayed by the display device. In general, touch screens can recognize a touch and the position of the touch on the touch sensor panel, and the computing system can then interpret the touch in accordance with the display appearing at the time of the touch, and thereafter can perform one or more actions based on the touch. In the case of some touch sensing systems, a physical touch on the display is not needed to detect a touch. For example, in some capacitive-type touch sensing systems, fringing electrical fields used to detect touch can extend beyond the surface of the display, and objects approaching near the surface may be detected near the surface without actually touching the surface.
Touch sensor panels can include an array of touch sensors capable of detecting touches (the touching by an object such as a finger upon a touch-sensitive surface). Some touch sensor panels are able to detect multiple touches (e.g., the touching of multiple fingers upon a touch-sensitive surface at distinct locations at or about the same time) and near touches (e.g., fingers within the near-field detection capabilities of their touch sensors), and identify and track their locations.
In reality, however, not all touches detected on a touch sensor panel are intended user input. For example, water droplets on the surface of the touch sensor panel can be detected as touches. In particular, water droplets that are capacitively coupled to ground via the housing or other conductive structures within a device can appear as a touch. As a result, water droplets can result in unintended behavior by the device. This can negatively affect user experience, particularly in wet environments.
BRIEF SUMMARY OF THE DISCLOSURE
This relates generally to improving touch detection in touch sensor panels, and more particularly to techniques for rejecting apparent (but false) touches caused by objects such as water droplets located in areas with parasitic capacitive paths to ground. In some examples, these capacitive paths to ground can be found in edge areas of touch panels located near device housings, which can be grounded through the body of a user touching the housing of the device. To minimize these false touches, one or more conductors can be located in proximity to the housing and driven with a stimulation signal to shield objects from being capacitively coupled to ground through the housing. In some examples, these conductors can be newly formed in proximity to the housing. In other examples, conductors already present in the product design can be configured to serve as a guard during touch sensing, and configured to perform its original function at other times.
In addition to providing these driven conductors to act as guards against objects being capacitively coupled to ground through the housing, in some examples various scans can be provided and compared to identify and reject apparent touches resulting from capacitive coupling to ground. In some examples, a non-bootstrapped scan can be performed in one scan step, where each of the touch nodes to be sensed can be simultaneously driven by a stimulation signal and sensed to obtain an image of touch, while other touch nodes that are not to be sensed (e.g., as in a coarse scan) can be grounded or held at a mid-rail voltage or at some other voltage. Alternatively, in some examples, a non-bootstrapped scan can be performed in multiple scan steps, where the touch sensor panel can be selectively separated into one or more sensed touch nodes and one or more non-sensed touch nodes (e.g., different touch nodes can be sensed or not sensed depending on the scan step). An image of touch can be obtained from the multi-step non-bootstrapped scan, during which time (for each step) the sensed touch nodes can be driven by a stimulation signal, and the non-sensed touch nodes can be grounded or held at a mid-rail voltage or at some other voltage. In some examples, a bootstrapped scan can be performed in one scan step, where each of the touch nodes of the touch sensor panel can be simultaneously driven by a stimulation signal and sensed. Alternatively, in some examples, a bootstrapped scan can be performed in multiple scan steps, where the touch sensor panel can be selectively separated into one or more sensed touch nodes and one or more non-sensed touch nodes (e.g., different touch nodes can be sensed or non-sensed depending on the scan step). An image of touch can be obtained from the multi-step bootstrapped scan, during which time (for each step) the sensed touch nodes can be driven by a stimulation signal, and the non-sensed touch nodes can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples an extended bootstrapped scan can also be performed, during which time the sensed touch nodes can be driven by a stimulation signal, and the guard conductor and the non-sensed touch nodes can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples, the results of the extended bootstrapped scan can be subtracted from the non-bootstrapped scan or the bootstrapped scan to identify and reject apparent (but false) touches (e.g., water droplets) resulting from parasitic capacitive coupling to ground.
BRIEF DESCRIPTION OF THE DRAWINGS
FIGS. 1A-1E
illustrate touch sensing devices or systems that can include a touch screen or touch sensor panel according to examples of the disclosure.
FIG. 2
illustrates a computing system including a touch screen according to examples of the disclosure.
FIG. 3A
illustrates a touch sensor circuit corresponding to a self-capacitance measurement of a touch node electrode and sensing circuit according to examples of the disclosure.
FIG. 3B
illustrates a touch sensor circuit corresponding to a mutual-capacitance drive line and sense line and sensing circuit according to examples of the disclosure.
FIG. 4A
illustrates a touch screen or touch sensor panel with touch electrodes arranged in rows and columns according to examples of the disclosure.
FIG. 4B
illustrates a touch screen or touch sensor panel with touch node electrodes arranged in a pixelated touch node electrode configuration according to examples of the disclosure.
FIG. 4C
illustrates a touch screen or touch sensor panel with touch node electrodes and corresponding routing arranged in a pixelated touch node electrode configuration according to examples of the disclosure.
FIG. 5
illustrates a representation of an image of touch according to examples of the disclosure.
FIG. 6
illustrates a representation of water droplets occurring in different areas on a touch surface according to examples of the disclosure.
FIG. 7A
illustrates a guarded conductor between a touch surface or substrate and a housing according to examples of the disclosure.
FIG. 7B
illustrates another guarded conductor between a touch surface or substrate and a housing according to examples of the disclosure.
FIG. 7C
illustrates another guarded conductor between a touch surface or substrate and a housing according to examples of the disclosure.
FIG. 7D
illustrates another guarded conductor between a touch surface or substrate and a housing according to examples of the disclosure.
FIG. 8A
illustrates a gasket which includes a guarded conductor between a touch surface or substrate and a housing according to examples of the disclosure.
FIG. 8B
illustrates a gasket according to examples of the disclosure.
FIG. 9A
illustrates a touch sensor panel with a finger touch in the inner area of the touch sensor panel, a finger touch in an edge area of the touch sensor panel, a water droplet in the inner area of the touch sensor panel, and a water droplet in the edge area of the touch sensor panel, where a non-bootstrapped (NBS) scan is being performed according to examples of the disclosure.
FIG. 9B
illustrates the touch sensor panel of
FIG. 9A
, except that in
FIG. 9B
, the touch sensor panel is performing a bootstrapped (BS) scan according to examples of the disclosure.
FIG. 9C
illustrates the touch sensor panel of
FIGS. 9A and 9B
, except that in
FIG. 9C
, the touch sensor panel is performing an extended bootstrapped (EBS) scan according to examples of the disclosure.
FIG. 10
illustrates a method and process for identifying and excluding apparent (but false) touches caused by parasitic capacitive coupling to ground according to examples of the disclosure.
DETAILED DESCRIPTION OF THE DISCLOSURE
In the following description of examples, reference is made to the accompanying drawings which form a part hereof, and in which it is shown by way of illustration specific examples that can be practiced. It is to be understood that other examples can be used and structural changes can be made without departing from the scope of the disclosed examples.
This relates generally to improving touch detection in touch sensor panels, and more particularly to techniques for rejecting apparent (but false) touches caused by objects such as water droplets located in areas with parasitic capacitive paths to ground. In some examples, these capacitive paths to ground can be found in edge areas of touch panels located near device housings, which can be grounded through the body of a user touching the housing of the device. To minimize these false touches, one or more conductors can be located in proximity to the housing and driven with a stimulation signal to shield objects from being capacitively coupled to ground through the housing. In some examples, conductors already present in the product design can be configured to serve as a guard during touch sensing, and configured to perform its original function at other times.
In some examples an image of touch can be obtained from a (single or multi-step) non-bootstrapped scan, during which time sensed touch nodes can be driven by a stimulation signal, and non-sensed touch nodes can be grounded or held at a mid-rail voltage or other voltage. In some examples an image of touch can be obtained from a (single or multi-step) bootstrapped scan, during which time sensed touch nodes can be driven by a stimulation signal, and non-sensed touch nodes (if any) can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples an extended bootstrapped scan can also be performed, during which time the sensed touch nodes can be driven by a stimulation signal, and the guard conductor and the non-sensed touch nodes (if any) can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples, the results of the extended bootstrapped scan can be subtracted from the non-bootstrapped scan or the bootstrapped scan to identify and reject apparent (but false) touches resulting from parasitic capacitive coupling to ground.
FIGS. 1A-1E
illustrate touch sensing devices or systems that can include a touch screen or touch sensor panel according to examples of the disclosure.
FIG. 1A
illustrates an example
mobile telephone
136
that can include a
touch screen
124
according to examples of the disclosure.
FIG. 1B
illustrates an example
digital media player
140
that can include a
touch screen
126
and/or a touch sensor panel according to examples of the disclosure.
FIG. 1C
illustrates an example
personal computer
144
that can include a
touch screen
128
and a track pad with a touch sensor panel according to examples of the disclosure.
FIG. 1D
illustrates an example
tablet computing device
148
that can include a
touch screen
130
according to examples of the disclosure.
FIG. 1E
illustrates an example wearable device
150
that includes a
touch screen
132
and can be attached to a user using a
strap
152
according to examples of the disclosure. It is understood that a touch screen (which can include a touch sensor panel) or a touch sensor panel (without a touch screen, such as in a trackpad) can be implemented in other devices as well, and that the example systems of
FIGS. 1A-1E
can further include touch sensor panels on surfaces not shown in the figures.
In some examples,
touch screens
124
,
126
,
128
,
130
and
132
and touch sensor panels can be can be based on self-capacitance. A self-capacitance based touch system can include a matrix of small, individual plates of conductive material or groups of individual plates of conductive material forming larger conductive regions that can be referred to as touch electrodes or as touch node electrodes (as described below with reference to
FIG. 4B
). For example, a touch screen or touch sensor panel can include a plurality of individual touch electrodes, each touch electrode identifying or representing a unique location (e.g., a touch node) on the touch screen or touch sensor panel at which touch or proximity is to be sensed, and each touch node electrode being electrically isolated from the other touch node electrodes in the touch screen/panel. Such a touch screen/panel can be referred to as a pixelated self-capacitance touch screen/panel, though it is understood that in some examples, the touch node electrodes on the touch screen/panel can be used to perform scans other than self-capacitance scans on the touch screen/panel (e.g., mutual capacitance scans). During operation, a touch node electrode can be stimulated with an alternating current (AC) waveform, and the self-capacitance to ground of the touch node electrode can be measured. As an object approaches the touch node electrode, the self-capacitance to ground of the touch node electrode can change (e.g., increase). This change in the self-capacitance of the touch node electrode can be detected and measured by the touch sensing system to determine the positions of multiple objects when they touch, or come in proximity to, the touch screen/panel. In some examples, the touch node electrodes of a self-capacitance based touch system can be formed from rows and columns of conductive material, and changes in the self-capacitance to ground of the rows and columns can be detected, similar to above. In some examples, a touch screen/panel can be multi-touch, single touch, projection scan, full-imaging multi-touch, capacitive touch, etc.
In some examples,
touch screens
124
,
126
,
128
,
130
and
132
and touch sensor panels can be based on mutual capacitance. A mutual capacitance based touch system can include electrodes arranged as drive and sense lines that may cross over each other on different layers (in a double-sided configuration), or may be adjacent to each other on the same layer (e.g., as described below with reference to
FIG. 4A
). The crossing or adjacent locations can form touch nodes. During operation, the drive line can be stimulated with an AC waveform and the mutual capacitance of the touch node can be measured. As an object approaches the touch node, the mutual capacitance of the touch node can change (e.g., decrease). This change in the mutual capacitance of the touch node can be detected and measured by the touch sensing system to determine the positions of multiple objects when they touch, or come in proximity to, the touch screen/panel. As described herein, in some examples, a mutual capacitance based touch system can form touch nodes from a matrix of small, individual plates of conductive material.
In some examples,
touch screens
124
,
126
,
128
,
130
and
132
or touch sensor panels can be based on mutual capacitance and/or self-capacitance. The electrodes can be arranged as a matrix of small, individual plates of conductive material (e.g., as in
touch node electrodes
408
in touch screen/
panel
402
in
FIG. 4B
) or as drive lines and sense lines (e.g., as in
row touch electrodes
404
and
column touch electrodes
406
in touch screen/
panel
400
in
FIG. 4A
), or in another pattern. The electrodes can be configurable for mutual capacitance or self-capacitance sensing or a combination of mutual and self-capacitance sensing. For example, in one mode of operation electrodes can be configured to sense mutual capacitance between electrodes and in a different mode of operation electrodes can be configured to sense self-capacitance of electrodes. In some examples, some of the electrodes can be configured to sense mutual capacitance therebetween and some of the electrodes can be configured to sense self-capacitance thereof.
FIG. 2
illustrates an example computing system including a touch screen according to examples of the disclosure, although it should be understood that the illustrated touch screen
220
(which includes a touch sensor panel) could instead be only a touch sensor panel.
Computing system
200
can be included in, for example, a mobile phone, tablet, touchpad, portable or desktop computer, portable media player, wearable device or any mobile or non-mobile computing device that includes a touch screen or touch sensor panel.
Computing system
200
can include a touch sensing system including one or
more touch processors
202
,
peripherals
204
, a
touch controller
206
, and touch sensing circuitry (described in more detail below).
Peripherals
204
can include, but are not limited to, random access memory (RAM) or other types of memory or storage, watchdog timers and the like.
Touch controller
206
can include, but is not limited to, one or
more sense channels
208
,
channel scan logic
210
and
driver logic
214
.
Channel scan logic
210
can access
RAM
212
, autonomously read data from the sense channels and provide control for the sense channels. In addition,
channel scan logic
210
can control
driver logic
214
to generate
stimulation signals
216
at various frequencies and/or phases that can be selectively applied to drive regions of the touch sensing circuitry of
touch screen
220
, as described in more detail below. In some examples,
touch controller
206
,
touch processor
202
and
peripherals
204
can be integrated into a single application specific integrated circuit (ASIC), and in some examples can be integrated with
touch screen
220
itself. The
example computing system
200
of
FIG. 2
can be configured to implement and perform any of the scans and comparisons described below.
It should be apparent that the architecture shown in
FIG. 2
is only one example architecture of
computing system
200
, and that the system could have more or fewer components than shown, or a different configuration of components. The various components shown in
FIG. 2
can be implemented in hardware, software, firmware or any combination thereof, including one or more signal processing and/or application specific integrated circuits.
Computing system
200
can include a
host processor
228
for receiving outputs from
touch processor
202
and performing actions based on the outputs. For example,
host processor
228
can be connected to
program storage
232
and a display controller/driver
234
(e.g., a Liquid-Crystal Display (LCD) driver). It is understood that although some examples of the disclosure may described with reference to LCD displays, the scope of the disclosure is not so limited and can extend to other types of displays, such as Light-Emitting Diode (LED) displays, including Organic LED (OLED), Active-Matrix Organic LED (AMOLED) and Passive-Matrix Organic LED (PMOLED) displays.
Display driver
234
can provide voltages on select (e.g., gate) lines to each pixel transistor and can provide data signals along data lines to these same transistors to control the pixel display image.
Host processor
228
can use
display driver
234
to generate a display image on
touch screen
220
, such as a display image of a user interface (UI), and can use
touch processor
202
and
touch controller
206
to detect a touch on or near
touch screen
220
, such as a touch input to the displayed UI. The touch input can be used by computer programs stored in
program storage
232
to perform actions that can include, but are not limited to, moving an object such as a cursor or pointer, scrolling or panning, adjusting control settings, opening a file or document, viewing a menu, making a selection, executing instructions, operating a peripheral device connected to the host device, answering a telephone call, placing a telephone call, terminating a telephone call, changing the volume or audio settings, storing information related to telephone communications such as addresses, frequently dialed numbers, received calls, missed calls, logging onto a computer or a computer network, permitting authorized individuals access to restricted areas of the computer or computer network, loading a user profile associated with a user's preferred arrangement of the computer desktop, permitting access to web content, launching a particular program, encrypting or decoding a message, and/or the like.
Host processor
228
can also perform additional functions that may not be related to touch processing.
Note that one or more of the functions described in this disclosure can be performed by firmware stored in memory (e.g., one of the
peripherals
204
in
FIG. 2
) and executed by
touch processor
202
, or stored in
program storage
232
and executed by
host processor
228
. The firmware can also be stored and/or transported within any non-transitory computer-readable storage medium for use by or in connection with an instruction execution system, apparatus, or device, such as a computer-based system, processor-containing system, or other system that can fetch the instructions from the instruction execution system, apparatus, or device and execute the instructions. In the context of this document, a “non-transitory computer-readable storage medium” can be any medium (excluding signals) that can contain or store the program for use by or in connection with the instruction execution system, apparatus, or device. In some examples,
RAM
212
or program storage
232
(or both) can be a non-transitory computer readable storage medium. One or both of
RAM
212
and
program storage
232
can have stored therein instructions, which when executed by
touch processor
202
or
host processor
228
or both, can cause the device including
computing system
200
to perform one or more functions and methods of one or more examples of this disclosure. The computer-readable storage medium can include, but is not limited to, an electronic, magnetic, optical, electromagnetic, infrared, or semiconductor system, apparatus or device, a portable computer diskette (magnetic), a random access memory (RAM) (magnetic), a read-only memory (ROM) (magnetic), an erasable programmable read-only memory (EPROM) (magnetic), a portable optical disc such a CD, CD-R, CD-RW, DVD, DVD-R, or DVD-RW, or flash memory such as compact flash cards, secured digital cards, USB memory devices, memory sticks, and the like.
The firmware can also be propagated within any transport medium for use by or in connection with an instruction execution system, apparatus, or device, such as a computer-based system, processor-containing system, or other system that can fetch the instructions from the instruction execution system, apparatus, or device and execute the instructions. In the context of this document, a “transport medium” can be any medium that can communicate, propagate or transport the program for use by or in connection with the instruction execution system, apparatus, or device. The transport medium can include, but is not limited to, an electronic, magnetic, optical, electromagnetic or infrared wired or wireless propagation medium.
Touch screen
220
can be used to derive touch information at multiple discrete locations of the touch screen, referred to herein as touch nodes.
Touch screen
220
can include touch sensing circuitry that can include a capacitive sensing medium having a plurality of
drive lines
222
and a plurality of sense lines
223
. It should be noted that the term “lines” is sometimes used herein to mean simply conductive pathways, as one skilled in the art will readily understand, and is not limited to elements that are strictly linear, but includes pathways that change direction, and includes pathways of different size, shape, materials, etc. Drive
lines
222
can be driven by
stimulation signals
216
from
driver logic
214
through a
drive interface
224
, and resulting sense signals
217
generated in
sense lines
223
can be transmitted through a
sense interface
225
to sense
channels
208
in
touch controller
206
. In this way, drive lines and sense lines can be part of the touch sensing circuitry that can interact to form capacitive sensing nodes, which can be thought of as touch picture elements (touch pixels) and referred to herein as touch nodes, such as
touch nodes
226
and
227
. This way of understanding can be particularly useful when
touch screen
220
is viewed as capturing an “image” of touch (“touch image”). In other words, after
touch controller
206
has determined whether a touch has been detected at each touch nodes in the touch screen, the pattern of touch nodes in the touch screen at which a touch occurred can be thought of as an “image” of touch (e.g., a pattern of fingers touching the touch screen). As used herein, an electrical component “coupled to” or “connected to” another electrical component encompasses a direct or indirect connection providing electrical path for communication or operation between the coupled components. Thus, for example, drive
lines
222
may be directly connected to
driver logic
214
or indirectly connected to drive
logic
214
via
drive interface
224
and
sense lines
223
may be directly connected to sense
channels
208
or indirectly connected to sense
channels
208
via
sense interface
225
. In either case an electrical path for driving and/or sensing the touch nodes can be provided.
FIG. 3A
illustrates an exemplary
touch sensor circuit
300
corresponding to a self-capacitance measurement of a
touch node electrode
302
and sensing circuit
314
(e.g., corresponding to a sense channel
208
) according to examples of the disclosure.
Touch node electrode
302
can correspond to a
touch electrode
404
or
406
of touch screen/
panel
400
or a
touch node electrode
408
of touch screen/
panel
402
.
Touch node electrode
302
can have an inherent self-capacitance to ground associated with it, and also an additional self-capacitance to ground that is formed when an object, such as
finger
305
, is in proximity to or touching the electrode. The total self-capacitance to ground of
touch node electrode
302
can be illustrated as
capacitance
304
.
Touch node electrode
302
can be coupled to
sensing circuit
314
.
Sensing circuit
314
can include an
operational amplifier
308
,
feedback resistor
312
and
feedback capacitor
310
, although other configurations can be employed. For example,
feedback resistor
312
can be replaced by a switched capacitor resistor in order to minimize a parasitic capacitance effect that can be caused by a variable feedback resistor.
Touch node electrode
302
can be coupled to the inverting input (−) of
operational amplifier
308
. An AC voltage source
306
(V
ac
) can be coupled to the non-inverting input (+) of
operational amplifier
308
.
Touch sensor circuit
300
can be configured to sense changes (e.g., increases) in the total self-
capacitance
304
of the
touch node electrode
302
induced by a finger or object either touching or in proximity to the touch screen/panel. Output
320
can be used by a processor to determine the presence of a proximity or touch event, or the output can be inputted into a discrete logic network to determine the presence of a proximity or touch event.
FIG. 3B
illustrates an exemplary
touch sensor circuit
350
corresponding to a mutual-
capacitance drive line
322
and
sense line
326
and sensing circuit
314
(e.g., corresponding to a sense channel
208
) according to examples of the disclosure.
Drive line
322
can be stimulated by stimulation signal
306
(e.g., an AC voltage signal).
Stimulation signal
306
can be capacitively coupled to
sense line
326
through
mutual capacitance
324
between
drive line
322
and the sense line. When a finger or object
305
approaches the touch node created by the intersection of
drive line
322
and
sense line
326
,
mutual capacitance
324
can change (e.g., decrease). This change in
mutual capacitance
324
can be detected to indicate a touch or proximity event at the touch node, as described herein. The sense signal coupled onto
sense line
326
can be received by sensing
circuit
314
.
Sensing circuit
314
can include
operational amplifier
308
and at least one of a
feedback resistor
312
and a
feedback capacitor
310
.
FIG. 3B
illustrates a general case in which both resistive and capacitive feedback elements are utilized. The sense signal (referred to as Vin) can be inputted into the inverting input of
operational amplifier
308
, and the non-inverting input of the operational amplifier can be coupled to a reference voltage V
ref
.
Operational amplifier
308
can drive its output to voltage V
o
to keep yin substantially equal to V
ref
, and can therefore maintain V
in
constant or virtually grounded. A person of skill in the art would understand that in this context, equal can include deviations of up to 15%. Therefore, the gain of
sensing circuit
314
can be mostly a function of the ratio of
mutual capacitance
324
and the feedback impedance, comprised of
resistor
312
and/or
capacitor
310
. The output of sensing circuit
314
V
O
can be filtered and heterodyned or homodyned by being fed into
multiplier
328
, where V
O
can be multiplied with
local oscillator
330
to produce V
detect
. V
detect
can be inputted into
filter
332
. One skilled in the art will recognize that the placement of
filter
332
can be varied; thus, the filter can be placed after
multiplier
328
, as illustrated, or two filters can be employed: one before the multiplier and one after the multiplier. In some examples, there can be no filter at all. The direct current (DC) portion of V
detect
can be used to determine if a touch or proximity event has occurred. Note that while
FIGS. 3A-3B
indicate the demodulation at
multiplier
328
occurs in the analog domain, output V
O
may be digitized by an analog-to-digital converter (ADC), and blocks
328
,
332
and
330
may be implemented in a digital fashion (e.g.,
328
can be a digital demodulator,
332
can be a digital filter, and
330
can be a digital NCO (Numerical Controlled Oscillator).
Referring back to
FIG. 2
, in some examples,
touch screen
220
can be an integrated touch screen in which touch sensing circuit elements of the touch sensing system can be integrated into the display pixel stack-ups of a display. The circuit elements in
touch screen
220
can include, for example, elements that can exist in LCD or other displays (LED display, OLED display, etc.), such as one or more pixel transistors (e.g., thin film transistors (TFTs)), gate lines, data lines, pixel electrodes and common electrodes. In a given display pixel, a voltage between a pixel electrode and a common electrode can control a luminance of the display pixel. The voltage on the pixel electrode can be supplied by a data line through a pixel transistor, which can be controlled by a gate line. It is noted that circuit elements are not limited to whole circuit components, such as a whole capacitor, a whole transistor, etc., but can include portions of circuitry, such as only one of the two plates of a parallel plate capacitor.
FIG. 4A
illustrates a touch screen or
touch sensor panel
400
with
touch electrodes
404
and
406
arranged in rows and columns according to examples of the disclosure. Specifically, touch screen/
panel
400
can include a plurality of
touch electrodes
404
disposed as rows, and a plurality of
touch electrodes
406
disposed as columns.
Touch electrodes
404
and
touch electrodes
406
can be on the same or different material layers on touch screen/
panel
400
, and can intersect with each other, as illustrated in
FIG. 4A
. In some examples, the electrodes can be formed on opposite sides of a transparent (partially or fully) substrate and from a transparent (partially or fully) semiconductor material, such as ITO, though other materials are possible. Electrodes displayed on layers on different sides of the substrate can be referred to herein as a double-sided sensor. In some examples, touch screen/
panel
400
can sense the self-capacitance of
touch electrodes
404
and
406
to detect touch and/or proximity activity on touch screen/
panel
400
, and in some examples, touch screen/
panel
400
can sense the mutual capacitance between
touch electrodes
404
and
406
to detect touch and/or proximity activity on
touch screen
400
.
FIG. 4B
illustrates a touch screen or
touch sensor panel
402
with
touch node electrodes
408
arranged in a pixelated touch node electrode configuration according to examples of the disclosure. Specifically, touch screen/
panel
402
can include a plurality of individual
touch node electrodes
408
, each touch node electrode identifying or representing a unique location on the touch screen/panel at which touch or proximity (i.e., a touch or proximity event) is to be sensed, and each touch node electrode being electrically isolated from the other touch node electrodes in the touch screen/panel, as previously described.
Touch node electrodes
408
can be on the same or different material layers on touch screen/
panel
402
. In some examples, touch screen/
panel
402
can sense the self-capacitance of
touch node electrodes
408
to detect touch and/or proximity activity on touch screen/
panel
402
, and in some examples, touch screen/
panel
402
can sense the mutual capacitance between
touch node electrodes
408
to detect touch and/or proximity activity on touch screen/
panel
402
.
FIG. 4C
illustrates a touch screen or
touch sensor panel
410
with touch node electrodes (e.g., including
touch node electrodes
422
,
424
,
426
,
428
and
430
) and corresponding routing (e.g., including
routing
428
A and
430
A) arranged in a pixelated touch node electrode configuration according to examples of the disclosure. Touch screen/
panel
410
can be similar to touch screen/
panel
402
, but can also illustrate corresponding routing of the touch node electrodes. Specifically, touch screen/
panel
410
can include a plurality of individual touch node electrodes, each touch node electrode identifying or representing a unique location on the touch screen/panel at which touch or proximity (i.e., a touch or proximity event) is to be sensed, and each touch node electrode being electrically isolated from the other touch node electrodes in the touch screen/panel, as previously described. The touch nodes can be routed to edges of the touch screen/panel
410
(and from the edges of the touch screen/
panel
410
to touch controller
206
). For example,
touch node electrode
428
can be routed to the edge of touch screen/
panel
410
via
routing trace
428
A and
touch node electrode
430
can be routed to the edge of touch screen/
panel
410
via
routing trace
430
A. The touch node electrodes and routing can be on the same material layer (as shown) or on different material layers (e.g., routing can be achieved via a different layer connected with vias) of touch screen/
panel
410
. In some examples, touch screen/
panel
410
can sense the self-capacitance of the touch node electrodes or the mutual capacitance between the touch node electrodes to detect touch and/or proximity activity on touch screen/
panel
410
.
FIG. 5
illustrates a representation of an image of touch according to examples of the disclosure. Touch screen/
panel
500
can include drive
lines
502
and
sense lines
504
arranged as a pattern of rows and columns, although other patterns can be possible.
Touch nodes
506
can be formed at the intersection between
drive lines
502
and
sense lines
504
, and the mutual capacitance (or change in mutual capacitance) therebetween can be measured. Each object touching or proximate to, but not touching, the touch screen/
panel
500
can produce a touch signal at
proximate touch nodes
506
. By processing the touch image, touch signals from proximate touch nodes
506
(e.g., those touch signals meeting a threshold signal level) can be grouped together to form
input patches
508
. Thus, the
input patches
508
can be regions within the image of touch corresponding to touch
nodes
506
having signal values produced by an object touching (or proximate to, but not touching, in some examples) the touch screen/
panel
500
. The input patches identified in a touch image can be tracked through multiple successive touch images. Input patches from a corresponding object captured across multiple touch images can be assigned to a corresponding path. Assigning input patches to paths can allow for tracking gesture inputs (e.g., swipe, pinch, etc.). In some examples, the path can track the input contact from an initial touchdown on the touch-sensitive surface through a liftoff from the touch-sensitive surface. In some examples, the input patches of a path can be analyzed to identify movement of the input patch across one or more touch images and thereby track movement of an object corresponding to the input patches. Although a path can be used to identify movement, some paths may not include movement (e.g., when the input patch remains in the same position from touchdown to liftoff, such as in a tap). The tracking can include tracking position, velocities, and/or geometries (e.g., shape, number of touch nodes) of the input patches from various touch images corresponding to a path.
As discussed above, a touch sensor panel can detect objects in contact with, or in proximity to, a touch surface. In capacitive touch sensor panels, the effect of capacitive coupling of the object with touch electrodes in the touch sensor panel can be detected by touch sensing circuitry. If the effect of the capacitive coupling is significant enough, the touch sensing circuitry can determine that a touch has occurred. In general, an object such as finger or stylus that is well-grounded can result in more charge being capacitively coupled from a touch node (in self-capacitance touch sensing systems) or a drive line (in mutual capacitance touch sensing systems) to the object, and then from the object to ground, than an object that is poorly grounded. In self-capacitance systems, this capacitive coupling can increase the touch node's self-capacitance to ground, while in mutual capacitance systems, this capacitive coupling can decrease the mutual capacitance between drive and sense lines. In either system, a well-grounded object is more likely to be recognized as a touch.
However, objects such as fingers and styli are not the only objects that can come into contact with a touch surface. For example, water droplets on a touch surface can exhibit characteristics similar to a finger or stylus, and can sometimes be erroneously recognized as an intended touch. When water droplets form in isolation on the surface of a touch sensor panel, they are generally floating with respect to ground or otherwise poorly grounded, and may not appear as a touch. However, water droplets near the edge of a touch sensor panel can be located close enough to a device housing such that significant capacitive coupling between the droplet and the housing can occur. Because the housing can be couplable to ground via a user's body, for example, the water droplets themselves can be grounded through the housing, and can erroneously be recognized as an intended touch. As a result, water can result in unintended behavior by the device, negatively affecting the user experience. (Note that although this disclosure may explicitly mention only water droplets for purposes of brevity, the scope of the disclosure is not so limited. References to water droplets herein are intended to be inclusive of other conductive substances such as oil, liquids, beverages and the like.)
In some examples, floating water droplets or partially grounded water droplets (e.g., droplets capacitively coupled to ground) can interfere with the accurate detection of intended user input such as a touchdown or a liftoff of an object (e.g., a finger). In some examples, floating or partially grounded water can interfere with the detection of a swipe gesture or cause a swipe gesture to be unintentionally canceled. In some examples, floating or partially grounded water can merge with an object (e.g., a finger) and cause offsets in centroid detection (creating unwanted jitter in the touch sensing system performance). In some examples, small droplets of water along the edges of a touch sensor panel can be detected as false taps or swipes, for example.
FIG. 6
illustrates a representation of water droplets occurring in different areas on a touch surface according to examples of the disclosure. In the example of
FIG. 6
,
water droplet
602
appearing on an interior area of
touch surface
600
can be ungrounded or poorly grounded and can be ignored as a touch (e.g., because the capacitive signal can be below a touch detection threshold). However, when a grounded finger or stylus contacts touch
surface
600
at
point
604
and makes contact with otherwise poorly grounded
water droplet
606
, a capacitive path to ground can develop from the water droplet to ground through the grounded object. As a result,
water droplet
606
can appear to be part of the touching object, and touch detection accuracy can be reduced. In addition, when
water droplet
608
at the edge of
touch surface
600
capacitively couples to a grounded housing, bezel, or other grounded conductor, a capacitive path to ground can develop from the water droplet to ground through the grounded housing, bezel or conductor. As a result,
water droplet
608
can appear to be a touching object, and device operations can be adversely impacted.
Note that although the problem of water droplets being capacitively coupled to ground and appearing to be an intended touch was described above with respect to a grounded housing, bezel or conductor, the problem can occur whenever a grounding path is present. For example, grounded conductors (such as grounded non-sensed touch nodes) within the interior area of the device can also produce enough capacitive coupling with the water droplet to cause the droplet to register as an intended touch.
To reduce the negative effects of parasitic capacitive paths to ground in touch sensor panels, non-sensed touch nodes (if any) can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples, a scan can be performed in one scan step, where each of the touch nodes of the touch sensor panel can be simultaneously driven by a stimulation signal and sensed. In other examples, a scan can be performed in multiple scan steps, where the touch sensor panel can be selectively separated into one or more sensed touch nodes and one or more non-sensed touch nodes (e.g., different touch nodes can be sensed or non-sensed depending on the scan step). Note that although examples of the disclosure may merely mention the driving of sensed and non-sensed touch nodes for purposes of brevity, it should be understood that this includes performing these scans in single or multiple steps. By bootstrapping the non-sensed touch nodes in this manner, the capacitive coupling between the sensed touch nodes and nearby non-sensed touch nodes (if any) can be greatly reduced. The non-sensed touch nodes can act as guards or shields to reduce the parasitic capacitive coupling between the sensed touch nodes and ground, which can serve to reduce the effect of noise on the sensed touch nodes. This bootstrapping technique can also cause floating water droplets to capacitively couple to the driven touch nodes instead of to ground, which reduces the likelihood that those droplets will be interpreted as intended touches. However, other objects, such as a finger, which can be grounded through other paths (such as through the user's body), can be unaffected (or be negligibly affected) by the stimulation applied to the non-sensed touch nodes. As a result, the guarded scan image (a bootstrapped image) can capture finger touches and exclude floating water.
On the other hand, a non-guarded scan image (a non-bootstrapped image) can be generated by applying the stimulation signal to the sensed touch nodes while grounding or applying a mid-rail voltage or other voltage to the non-sensed touch nodes. As a result, objects such as floating water can be capacitively coupled to ground via the non-sensed touch nodes. Thus, the non-guarded scan image can capture both fingers and floating water, because both can be grounded (or have a relatively low impedance path to ground). Taking a difference between the guarded and non-guarded scan images can result in an image that includes floating water droplets but excludes touches from well-grounded objects (e.g., fingers, styli, etc.). The identified water droplets can then be removed from subsequent touch image processing.
Although the use of guarded scans can reduce the capacitive coupling of a water droplet to ground in the interior regions of a touch screen or touch sensor panel, capacitive paths to ground can still exist at the edges of the touch screen/panel, where no guarded non-sensed touch nodes may be present. For example, a droplet can capacitively couple to ground through the housing of a device, if the housing is in contact with a grounded user. Additionally or alternatively, a droplet can capacitively couple to ground through another grounded conductor near the edge of the touch screen/panel that is not guarded by a driven non-sensed touch node. These paths to ground can be reduced if a guarded conductor, driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes, can be positioned to at least partially cover and guard or shield the grounded housing.
FIG. 7A
illustrates a guarded
conductor
708
located between a touch surface or
substrate
700
and a
housing
704
according to examples of the disclosure. In the example of
FIG. 7A
, a portion of touch surface or substrate
700
(i.e., a cover glass, crystal, plastic, etc.) attached to underlying
touch sensor panel
702
can be assembled in close proximity to
housing
704
.
Touch nodes
710
can be formed in
touch sensor panel
702
in proximity to touch
surface
700
to create an active touch area, and can be configurable to be driven with stimulation signals.
Touch nodes
710
can be selectively separable into one or more sensed touch nodes (i.e., those touch nodes whose touch signals are being measured) and one or more non-sensed touch electrodes (i.e., these touch nodes whose touch signals are not being measured). In some examples, each touch node in the touch sensor panel can be sensed simultaneously.
When housing
704
is grounded (e.g., the housing can be couplable to ground through a user's body), capacitance CB can form between
water droplet
706
and the
housing
704
. In the example of
FIG. 7A
, at least a portion of
conductor
708
can be disposed partially or fully between touch surface or
substrate
700
and
housing
704
, outside or beyond the active touch area.
Conductor
708
can be distinct from the touch nodes, electrically insulated from the housing, and configurable to be driven (e.g., during touch sensing) with a stimulation signal that has the same characteristics as the stimulation signal being applied to some of the touch nodes. For example,
conductor
708
may receive a stimulation signal that has the same amplitude, frequency and phase as a stimulation signal being applied to non-sensed touch nodes, though not generated from exactly the same source output as the stimulation signal being applied to the non-sensed touch nodes. In this manner, capacitance CA can form between
droplet
706
and
conductor
708
, instead of (or reducing the amount of capacitive coupling) between
droplet
706
and the grounded
housing
704
. Because
conductor
708
is biased at the same potential as the sensed touch nodes and not to ground, less charge is coupled between the droplet to ground. This can result in less charge coupling between
touch node
710
to
droplet
706
, which in turn results in a smaller change in the touch signal appearing at
touch node
710
, and a reduced likelihood of the apparent (but false) touch being detected as intended touch.
In various non-limiting examples,
conductor
708
can be alternatively formed as a flex circuit, deposited onto touch surface or
substrate
700
or (indirectly) onto
housing
704
, or formed within a gasket, as long as the conductor is insulated from ground. Note that although the example of
FIG. 7A
shows
conductor
708
extending along the full length of the gap between touch surface or
substrate
700
and
housing
704
, in other examples the conductor can only partially extend along the gap, with diminished effectiveness but with the potential benefit of easier and lower cost fabrication and assembly.
FIG. 7B
illustrates another guarded
conductor
708
between touch surface or
substrate
700
and
housing
704
according to examples of the disclosure. The example of
FIG. 7B
is similar to that of
FIG. 7A
, albeit with a different configuration of touch surface or substrate and housing.
FIG. 7C
illustrates another guarded
conductor
708
between touch surface or
substrate
700
and
housing
704
according to examples of the disclosure. In the example of
FIG. 7C
,
conductor
708
can be formed on the same side of touch surface or
substrate
700
as
touch nodes
710
, and can even be formed in the same layer as the touch nodes, which can result in lower cost fabrication and assembly. In another example,
conductor
708
can be an extension of a driven shield layer on the underside of touch surface or
substrate
700
. In other examples,
conductor
708
can be formed on
touch sensor panel
702
to perform other functions, but can be driven with a stimulation signal to serve as a guarded conductor during touch sensing.
FIG. 7D
illustrates another guarded conductor between touch surface or
substrate
700
and
housing
704
according to examples of the disclosure. The example of
FIG. 7D
is similar to that of
FIG. 7C
, albeit with a different configuration of touch surface or substrate and housing. In the example of
FIG. 7D
,
conductor
708
can be formed on top of touch surface or
substrate
700
, which can result in lower cost fabrication and assembly. In other examples,
conductor
708
can be formed on the top of touch surface or
substrate
700
to perform other functions, but can be driven with a stimulation signal to serve as a guarded conductor during touch sensing.
As noted above, in some examples of the disclosure, rather than adding a new driven conductor, existing conductors can be configured to be multi-functional and driven with a stimulation signal at selected times (e.g., during touch sensing) to achieve a similar effect as a new driven conductors.
FIG. 8A
illustrates
gasket
812
which includes guarded
conductor
808
installed between touch surface or
substrate
800
and
housing
804
according to examples of the disclosure. In the example of
FIG. 8A
, a portion of touch surface or
substrate
800
attached to an underlying
touch sensor panel
802
can be assembled in close proximity to
housing
804
. In some examples,
gasket
812
can be installed between at least a portion of touch surface or
substrate
800
and
housing
804
. In some examples,
gasket
812
can perform the function of environmentally sealing the interior of the device. In some examples,
gasket
812
can include force sensing layers to detect force being applied to touch surface or
substrate
800
. In some examples,
gasket
812
can further include
top shield layer
808
to shield the force sensing layers. In some examples, this
top shield layer
808
is configurable and can be biased at a particular potential (e.g., grounded) during certain modes of operation (e.g., force sensing).
When
water droplet
806
is present on touch surface or
substrate
800
, a capacitance CB can form between the droplet and
housing
804
, particularly if the housing is grounded. A capacitance C
NODE
can also form between
droplet
806
and
touch node
810
. If
top shield layer
808
is grounded during touch sensing, it would provide another undesirable (parasitic) capacitive path CA to ground, and could be another contributor to the total capacitance to ground seen by
droplet
806
.
However, according to some examples of the disclosure, during touch sensing
top shield layer
808
can instead be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In this manner, capacitance CA can form between
droplet
806
and
top shield layer
808
, instead of between
droplet
806
and grounded
housing
804
. Because
top shield layer
808
is biased at the same potential as the sensed touch nodes and not to ground, less charge is coupled from the droplet to ground through housing
804
(though capacitance CB may still be present). This can result in less charge coupling from
touch node
810
to
droplet
806
, which in turn results in a smaller change in the touch signal appearing at
touch node
810
, and a reduced likelihood of the apparent (but false) touch being detected as intended touch. In essence,
top shield layer
808
can be either grounded or driven with the stimulation signal to serve two different shielding functions at different times.
FIG. 8B
illustrates
gasket
812
according to examples of the disclosure. In the example of
FIG. 8B
, gasket can include
top shield layer
808
, force sensing layers
814
and
816
separated by flexible
dielectric material
818
, and
lower shield layer
820
. As described above, in some examples
top shield layer
808
can be grounded during force sensing, and driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. However, in other examples, any of the other layers of
gasket
812
can be alternatively or additionally driven with the stimulation signal, as long as no layer is grounded and is exposed to the droplet without an intervening driven layer. For example,
layer
816
could be used as the stimulated layer, as long as
layers
808
and
814
were floated and not grounded. It should be understood that the stackup of
FIG. 8B
is only exemplary, and that gaskets having fewer or different conductive layers can also be employed.
In various examples, driving
top shield layer
808
or any of the other conductive layers in
gasket
812
with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes during touch sensing may require that those conductors be configurable under program control (e.g., by
host processor
228
,
touch controller
206
, etc.) to be driven with different signals at different times. In such examples, the layers of
gasket
812
may be connected to a touch controller circuit to implement these different configurations. In the examples of
FIGS. 8A and 8B
, touch sensing can be time-multiplexed with force sensing, so that force sensing can be performed with gasket
812
(with
top shield layer
808
grounded, for example), and touch sensing can be performed (with top shield layer being stimulated, for example) during non-overlapping times.
FIG. 9A
illustrates
touch sensor panel
900
with finger touch (patch)
902
in an inner area of the touch sensor panel, finger touch (patch)
904
in an edge area of the touch sensor panel, water droplet (patch)
906
in the inner area of the touch sensor panel, and water droplet (patch)
908
in the edge area of the touch sensor panel according to examples of the disclosure. In the example of
FIG. 9A
, touches are represented symbolically with solid line circles, and droplets are represented symbolically with dashed line circles, where the size of the circles is intended to represent the strength or magnitude of the touch signals, and not the area of the touch or droplet. In the example of
FIG. 9A
,
touch sensor panel
900
is being subjected to a non-bootstrapped (NBS) scan, where sensed touch nodes are driven with a stimulation signal, and non-sensed touch nodes are grounded or held at a mid-rail voltage or other fixed voltage. Because finger touches
902
and
904
are well-grounded, they can register as strong touches (e.g., touch signals exceeding a particular threshold).
Droplet
906
may be otherwise floating, but because the non-sensed electrodes are grounded (or held at a fixed voltage),
droplet
906
can be capacitively coupled to ground through those non-sensed electrodes (if any) and can register as a moderate touch (e.g., touch signals within a particular threshold range below the strong touch threshold) relative to the finger touches.
Droplet
908
may also be otherwise floating, but because the non-sensed electrodes are grounded (or held at a fixed voltage) and
droplet
908
can be capacitively coupled to ground through a nearby grounded housing,
droplet
908
can also register as a moderate touch.
FIG. 9B
illustrates the
touch sensor panel
900
of
FIG. 9A
, except that in
FIG. 9B
, the touch sensor panel is performing a bootstrapped (BS) scan according to examples of the disclosure. In a BS scan, sensed touch nodes are driven with a stimulation signal, and non-sensed touch nodes (if any) are also driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. Because finger touches
902
and
904
are well-grounded, they can register as strong touches.
Droplet
906
may be otherwise floating, but because the non-sensed electrodes (if any) are stimulated rather than grounded,
droplet
906
may not be capacitively coupled to ground (or may be weakly capacitive coupled to ground) and can register as a very slight touch or no touch at all (e.g., touch signals below the threshold range of a moderate touch) relative to the finger touches.
Droplet
908
is also floating, but because
droplet
908
is capacitively coupled to ground through the nearby grounded housing,
droplet
908
can register as a moderate touch.
FIG. 9C
illustrates the
touch sensor panel
900
of
FIGS. 9A and 9B
, except that in
FIG. 9C
, the touch sensor panel is performing an extended bootstrapped (EBS) scan according to examples of the disclosure. In an EBS scan, sensed touch nodes are driven with a stimulation signal, non-sensed touch nodes (if any) are also driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes, and a conductor near the housing is also driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. This conductor can be any of the example conductors illustrated in
FIGS. 7A-7D and 8A-8B
. Because finger touches
902
and
904
are well-grounded, they can register as strong touches.
Droplet
906
may be otherwise floating, but because the non-sensed electrodes (if any) are stimulated,
droplet
906
may not be (or may weakly be) capacitively coupled to ground and can register as a very slight touch, or no touch at all.
Droplet
908
may also be otherwise floating, but because the non-sensed electrodes and also the conductor are driven with the stimulation signal,
droplet
908
may not be (or may weakly be) capacitively coupled to ground and can register as a very slight touch or no touch at all.
As
FIGS. 9A-9C
illustrate, different types of scans can enable the touch sensing system to identify touch signals or input patches meeting one or more characteristics that can indicate the presence of floating water droplets, and also water droplets that are capacitively coupled to ground. In one example, a comparison of
FIGS. 9A and 9B
can reveal differences between the NBS and BS scans. In particular, the touch signals corresponding to droplet
906
are stronger in
FIG. 9A
due to the grounded non-sensed touch nodes providing a capacitive path to ground for
droplet
906
, and weaker in
FIG. 9B
due to the non-sensed touch nodes being driven by a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. Thus, the NBS-BS comparison can indicate the presence of floating water droplets, particularly those floating water droplets that are capacitively coupled to ground primarily through non-sensed touch nodes, and not through other paths such as a grounded (or fixed voltage) shield layer in a gasket, for example.
In another example, a comparison of
FIGS. 9A and 9C
can reveal differences between the NBS and EBS scans. In particular, the touch signals corresponding to droplet
908
are stronger in
FIG. 9A
due to the grounded (or fixed voltage) shield layer in the gasket providing a capacitive path to ground for
droplet
908
, and weaker in
FIG. 9C
due to the shield layer in the gasket being driven by a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. The touch signals corresponding to droplet
906
are stronger in
FIG. 9A
due to the grounded (or fixed voltage) non-sensed touch nodes providing a capacitive path to ground for
droplet
906
, and weaker in
FIG. 9C
due to the non-sensed touch nodes being driven by a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. Thus, the NBS-EBS comparison can indicate the presence of floating water droplets, particularly those floating water droplets that are capacitively coupled to ground through non-sensed touch nodes or a shield layer in a gasket, for example. In another example, a comparison of
FIGS. 9B and 9C
can reveal differences between the BS and EBS scans. In particular, the touch signals corresponding to droplet
908
are stronger in
FIG. 9B
due to the grounded (or fixed voltage) shield layer in the gasket providing a capacitive path to ground for
droplet
908
, and weaker in
FIG. 9C
due to the shield layer in the gasket being driven by a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. Thus, the BS-EBS comparison can indicate the presence of floating water droplets, particularly those floating water droplets that are capacitively coupled to ground primarily through paths such as a grounded (or fixed voltage) shield layer in a gasket, for example.
Therefore, in one example, by subtracting the touch image generated from the EBS scan from the touch image generated from the NBS scan, only the touch signals associated with
droplets
906
and
908
remain, and it can be determined that the touch signals associated with
droplets
906
and
908
in
FIG. 9A
should be excluded as false touches caused by the capacitive paths to ground through grounded (or fixed voltage) non-sensed touch nodes, a grounded shield layer in a gasket, or a grounded housing, for example. In another example, by subtracting the touch image generated from the EBS scan from the touch image generated from the BS scan, only the touch signal associated with
droplet
908
remains, and it can be determined that the touch signal associated with
droplet
908
in
FIG. 9B
should be excluded as a false touch caused by a grounded shield layer in a gasket or a grounded housing, for example. In other examples, other combinations of the EBS scan and the NBS or BS scans can generally be used to identify and exclude apparent touches that are influenced by grounding paths in the interior or at the edges of a device. For example, touch signals at individual touch nodes in the BS and EBS scans can be added together, and if the sum does not equal approximately double (e.g., within a threshold amount) the touch signal obtained during the BS scan, it can be concluded that the touch node was influenced by a grounding path during the BS scan and should excluded as an intended touch. In other examples, touch signals at individual touch nodes in the BS and EBS scans can be averaged, and if the average does not equal approximately half (e.g., within a threshold amount) the touch signal obtained during the BS scan, it can be concluded that the touch node was influenced by a grounding path during the BS scan and should excluded as an intended touch. Similar combinations or comparisons of touch signals at touch nodes in the NBS and EBS scans can also be utilized to identify and exclude apparent (but false) touches caused by touch nodes influenced by parasitic grounding paths in the device.
Because the difference in the BS and EBS scans occurs primarily in the edge regions, in some examples the comparisons of the BS and EBS scans can be limited to touch signals of touch nodes in predetermined edge regions. In some examples, the edge regions can be empirically determined, for a particular touch panel/housing design, to be those regions where sufficient parasitic capacitive paths to ground exist to cause ungrounded objects to effect some threshold amount of change in the touch signals of touch nodes (e.g., halfway between a baseline no-touch signal level and a recognized touch signal level). In other examples, if no apparent touch is detected in the predetermined edge region in the BS scan, it can be concluded that there are no touch nodes that could have been influenced by a grounding path during the BS scan, and no comparison of the BS and EBS scans needs to be performed in any region of the touch sensor panel (e.g., forgo the EBS scan entirely or forgo the comparison to reduce unnecessary processing).
In some examples of the disclosure, after certain apparent (but likely false) touches are identified for exclusion, all apparent touches in the original NBS or BS image can be assigned identifiers or otherwise tagged, indicating that the apparent touches are either to be further processed or excluded from further processing. In other examples, the touch signals in the original NB S or BS image can be modified to remove the apparent (but likely false) touches prior to further processing.
FIG. 10
illustrates a method and process for identifying and excluding apparent (but false) touches caused by parasitic capacitive coupling to ground according to examples of the disclosure. In the example of
FIG. 10
, an NBS or BS scan can be performed at
1002
where in the NBS scan sensed touch nodes can be driven with a stimulation signal and non-sensed touch nodes can be held at ground (or a fixed voltage), and in the BS scan sensed touch nodes can be driven with a stimulation signal and non-sensed touch nodes (if any) can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes.
At
1004
(in dashed lines to indicate the optional nature of this step), one or more areas capable of providing one or more capacitive paths to ground that may not be adequately shielded by driven touch nodes can be identified. In some examples, these areas can include a grounded conductive layer located between a touch surface and a housing, a housing capable of becoming grounded, or other areas located at the perimeter of, or outside, a touch sensor panel such that a capacitive path to ground can exist with objects on the touch sensor panel even if the touch nodes in the panel are driven with stimulation signals in a BS scan.
At
1006
(in dashed lines to indicate the optional nature of this step), one or more conductors capable of being driven with a stimulation signal to guard against capacitive paths to ground can be identified. In some examples, the conductors can be existing conductors located in proximity to a housing having a particular function that can be driven during touch sensing to provide the desired guard function. Because conductors that are grounded for other functions can exacerbate the problem of providing parasitic capacitive coupling paths to ground, in some examples ideal candidates can be conductors that are normally grounded to perform some function but can be temporarily stimulated instead of being grounded. In other examples, the conductors may be newly added to the product design in proximity to the housing.
At
1008
, an EBS scan can be performed where sensed touch nodes can be driven with a stimulation signal, non-sensed touch nodes (if any) can be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes, and one or more of the conductors (optionally identified at
1006
) can also be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the sensed touch nodes. In some examples, these conductors can be driven during times when stimulating the conductors does not interfere with other operations that may require or prefer that these conductors be grounded (or held at a fixed voltage).
At
1010
, the results of the NBS and EBS scans at
1002
and
1008
can be compared to identify input patches in the NBS scan that were the result of one or more capacitive paths to ground in the device (and not through a touching or proximate object). Additionally or alternatively the results of the BS and EBS scans at
1002
and
1008
can be compared, at
1010
, to identify input patches in the BS scan that were the result of one or more capacitive paths to ground in the device (and not through a touching or proximate object) that were not shielded by the driven touch nodes during the BS scan (e.g., a capacitive path to ground through a shield in a gasket, through a grounded housing etc.). In some examples, this comparison can include subtracting the EBS scan from the NBS scan or the BS scan. In other examples, this comparison can include adding or averaging the results of the EBS scan and the NBS scan or the BS scan and using different thresholds to identify these input patches.
At
1012
, contacts in the NBS scan that were identified as being the result of one or more capacitive paths to ground in the device (and not through a touching or proximate object) can be excluded from further processing, or contacts in the BS scan that were identified as being the result of one or more capacitive paths to ground in the device (and not through a touching or proximate object) that were not shielded by the driven touch nodes during the BS scan (e.g., a capacitive path to ground through a shield in a gasket, though a grounded housing, etc.) can be excluded from further processing.
The example NBS, BS and EBS scans and comparisons described above can be implemented with self-capacitance touch sensor panels and touch nodes. However, droplets that are capacitively coupled to ground can also present problems for mutual capacitance touch sensor panels, because they can also appear to be touches. Therefore, in some mutual capacitance examples of the disclosure, the conductors identified in
block
1006
of
FIG. 10
can also be driven with a stimulation signal that has the same characteristics as the stimulation signal being applied to the drive lines in a mutual capacitance touch sensor panel. Driving the conductor areas with a stimulation signal may, in some circumstances (when non-stimulated drive lines are not providing a capacitive grounding path), reduce a droplet's capacitive coupling to ground and cause the droplets to be less visible as apparent touches, even during mutual capacitance touch sensing.
Therefore, according to the above, some examples of the disclosure are directed to a touch sensing device comprising a housing configured to be couplable to ground, a touch surface in proximity to the housing, touch nodes in proximity to the touch surface and configurable to be driven with a first stimulation signal, and one or more conductors distinct from the touch nodes and electrically insulated from the housing. At least a portion of the one or more conductors can be positioned between the touch surface and the housing and configurable to be driven with a second stimulation signal having the same characteristics as the first stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch nodes are selectively separable into one or more sensed touch nodes and one or more non-sensed touch nodes, the one or more sensed touch nodes are configured to receive the first stimulation signal, and the one or more non-sensed touch nodes and the one or more conductors are configured to receive the second stimulation signal having the same characteristics as the first stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch nodes form an active touch area on the touch surface, and the one or more conductors are located at least partially outside the active touch area. Additionally or alternatively to one or more of the examples disclosed above, in some examples the one or more conductors are configurable to be biased at a first potential in a first mode of operation, and driven with the second stimulation signal in a touch sensing mode of operation. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch nodes and the one or more conductors are formed in a same layer. Additionally or alternatively to one or more of the examples disclosed above, in some examples the one or more conductors are an extension of one or more driven shield layers in proximity to the active touch area, the one or more conductors extending the one or more shield layers beyond the active touch area. Additionally or alternatively to one or more of the examples disclosed above, in some examples the one or more conductors are formed in one or more gaskets configured for sealing the touch sensing device. Additionally or alternatively to one or more of the examples disclosed above, in some examples at least one of the gaskets comprises one or more force sensors configured for detecting force applied to the touch surface. Additionally or alternatively to one or more of the examples disclosed above, in some examples the first mode of operation is a shielding operation and the one or more conductors are configurable for being grounded when performing the shielding operation. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch sensing device further comprises a touch controller communicatively coupled with the touch nodes and the one or more conductors and configured for generating the first stimulation signal and the second stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch sensing device further comprises a touch controller communicatively coupled with the touch nodes and the one or more conductors and configured for driving the one or more sensed touch nodes with the first stimulation signal, and driving the one or more non-sensed touch nodes and the one or more conductors with the second stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the touch sensing device further comprises a touch controller communicatively coupled with the touch nodes and the one or more conductors and configured for biasing the one or more conductors at the first potential in the first mode of operation and driving the one or more conductors with the second stimulation signal in the touch sensing mode of operation.
Some examples of the disclosure are directed to a method of operating a touch sensing device, comprising shielding one or more objects appearing on a touch surface of the touch sensing device from capacitively coupling to ground through a housing of the touch sensing device, wherein the shielding includes driving at least a portion of one or more conductors with a second stimulation signal having the same characteristics as a first stimulation signal driving one or more touch nodes in the touch sensing device, and wherein the one or more conductors are located in proximity to the housing but at least partially outside an active touch area defined by the touch nodes. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises stimulating one or more sensed touch nodes of the touch nodes with the first stimulation signal, and stimulating one or more non-sensed touch nodes of the touch nodes with the second stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises identifying at least one of the conductors as being grounded while performing a first function during a first time period and utilizing the conductive material as the one or more conductors driven by the second stimulation signal for a second function during a second time period. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises biasing the one or more conductors at a first potential in a first mode of operation, and driving the one or more conductors with the second stimulation signal in a touch sensing operation. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises forming the plurality of touch nodes and the one or more conductors in a same layer. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises forming the one or more conductors in one or more gaskets configured for sealing the touch sensing device. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises detecting force applied to touch surface using one or more force sensors in at least one of the gaskets. Additionally or alternatively to one or more of the examples disclosed above, in some examples the first mode of operation is a shielding operation and the one or more conductors are configurable for being grounded when performing the shielding operation. Additionally or alternatively to one or more of the examples disclosed above, in some examples a non-transitory computer readable storage medium stores instructions that when executed by a touch sensing device, cause the touch sensing device to perform the method of one or more of the examples disclosed above.
Some examples of the disclosure are directed to a method of operating a touch sensing device, comprising performing a first scan of touch nodes of the touch sensing device by driving sensed touch nodes with a first stimulation signal, the first scan including first touch signals grouped into first patches indicative of objects capacitively coupled to ground, performing a second scan of the touch nodes by driving the sensed touch nodes with the first stimulation signal while shielding against capacitive coupling paths to ground through the touch sensing device, the second scan including second touch signals grouped into second patches indicative of objects capacitively coupled to ground through the one or more objects, and comparing the first and second scans to determine which of the first patches are indicative of objects capacitively coupled to ground through the touch sensing device. Additionally or alternatively to one or more of the examples disclosed above, in some examples the first scan further includes holding non-sensed touch nodes at a fixed potential. Additionally or alternatively to one or more of the examples disclosed above, in some examples the first scan further includes driving non-sensed touch nodes with a second stimulation signal having the same characteristics as the first stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples shielding against capacitive coupling paths to ground through the touch sensing device in the second scan comprises driving conductors located at least partially in proximity to a housing of the touch sensing device with the second stimulation signal. Additionally or alternatively to one or more of the examples disclosed above, in some examples the method further comprises excluding the first patches indicative of objects capacitively coupled to ground through the touch sensing device from further touch processing. Additionally or alternatively to one or more of the examples disclosed above, in some examples a non-transitory computer readable storage medium stores instructions that when executed by a touch sensing device, cause the touch sensing device to perform the method of one or more of the examples disclosed above. Additionally or alternatively to one or more of the examples disclosed above, in some examples a touch sensing device can be configured to perform the method of one or more of the examples disclosed above.
Although examples of this disclosure have been fully described with reference to the accompanying drawings, it is to be noted that various changes and modifications will become apparent to those skilled in the art. Such changes and modifications are to be understood as being included within the scope of examples of this disclosure as defined by the appended claims.
