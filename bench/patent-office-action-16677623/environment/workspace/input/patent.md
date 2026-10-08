## Metadata

- Application Number: 16677623
- Title: Providing a Continuity of Care Across Multiple Care Settings
- Filing Date: 2019-11-07
- Dataset Category: A

## Inventors / Authors

- Martin F. BURNS

## Classification

- Main CPC: A61B5/443
- Main IPC: Not available

## Abstract

The present disclosure provides methods of providing a continuity of care for a patient during transfer between care settings. The method includes the steps of deciding to transfer a patient from a first care setting to a second care setting, performing a first assessment of the patient in the first care setting, preparing a transfer record of the assessment, and transferring the transfer record with the patient to the second care setting.

## Initial Submission Claims

We claim:

1\. A method of providing a continuity of care for a patient during transfer between care settings, the method comprising the steps of deciding to transfer a patient from a first care setting to a second care setting, performing a first assessment of the patient in the first care setting, preparing a transfer record of the assessment, and
transferring the transfer record with the patient to the second care setting.

2\. The method of claim 1, wherein the first assessment comprises performing a sub- epidermal moisture (SEM) scan of at least one body location of the patient.

3\. The method of claim 2, wherein the SEM scan comprises a plurality of measurements of an SEM value at the body location and calculation of a delta value from the plurality of SEM values.

4\. The method of claim 3, further comprising the step of:
performing a plurality of SEM scans of the patient at different times while in the first care setting, and
recording the delta values from each of the respective SEM scans, wherein the decision to transfer the patient is based partially on the delta values recorded while in the first care setting.

5\. The method of claim 4, wherein the transfer record comprises the delta values from a portion of the plurality of SEM scans of the patient taken at different times while in the first care setting.

6\. The method of claim 2, wherein the SEM scan is performed at all body locations identified for monitoring.

7\. The method of claim 1, wherein the first assessment comprises at least one of a risk assessment of the patient, a visual skin assessment of at least one body location of the patient, and an image of the at least one body location.

8\. The method of claim 1, wherein the transfer record comprises at least one of a transaction type, a transaction date/time, a "to" location, and a "from" location.
9\. The method of claim 1, further comprising the steps of performing a first SEM scan of at least one body location of the patient while in the first care setting, wherein the first SEM scan comprises a plurality of measurements of an SEM value at the body location and calculation of a first delta value from the plurality of SEM values, creating a first data record that comprises the first delta value, reporting the first data record to a database, and
reporting the transfer record to the database.

10\. The method of claim 9, wherein:
the first data record comprises a patient identifier and a first date/time when the first SEM scan was performed, and
the transfer record comprises the patient identifier and a second date/time when the first assessment was performed.

11\. The method of claim 10, further comprising the steps of:
performing an SEM scan of the at least one body location of the patient and calculating a second delta value while in the second care setting, creating a second data record that comprises the patient identifier, the second delta value, and a third date/time when the second SEM scan was performed, and
reporting the second data record to a database.

12\. The method of claim 11, further comprising the step of:
querying the database to retrieve a portion of data records that comprise the delta values of the at least one body location of the patient.

13\. The method of claim 12, further comprising the step of:
formatting the retrieved delta values in date/time order, and
displaying the formatted delta values.

14\. The method of claim 10, further comprising the steps of:
creating an additional data record that comprises the patient identifier, a data element from the group of nutritional information, an implemented intervention, a risk assessment, a visual skin assessment, a care plan, a doctor's note, lean event, a vital sign, a body weight, and a lab result, and a date/time associated with the data element, and
reporting the additional data record to the database.

15\. The method of claim 13, wherein the formatted delta values is displayed in the form of a curve.

16\. The method of claim 15, further comprising the step of analyzing the retrieved delta values to determine one or more of a slope, an acceleration, a curve shape and associated characteristics, and a time-to-intercept of a selected threshold value.

17\. The method of claim 16, wherein acceleration is determined by the rate of change of the slope of the curve.

18\. The method of claim 16, wherein the decision to transfer the patient is based partially on one or more of the slope, the acceleration, the curve shape and associated characteristics, and the time-to-intercept of a selected threshold value.

19\. The method of claim 11, further comprising the steps of. performing an SEM scan of the at least one body location of the patient and calculating a third delta value while in the third care setting, creating a third data record that comprises the patient identifier, the third delta value, and a fourth date/time when the third SEM scan was performed, and
reporting the third data record to a database.

20\. The method of claim 19, further comprising the step of querying the database to retrieve the delta values observed over time for a particular patient across multiple care settings and various episodes of care. 41 42 43 US 166932975v1

## Description

CROSS-REFERENCE TO RELATED APPLICATIONS
This application claims benefit of U.S. Provisional Application No. 62/587,337, which was filed Nov. 16, 2017 and U.S. Provisional Application No. 62/693,810, which was filed Jul. 3, 2018. The entire content of these applications is incorporated herein by reference.
FIELD
The present disclosure provides methods of transferring and handling patient information, in particular information related to the risk of developing a pressure ulcer, to improve care when a patient receives care in multiple settings.
BACKGROUND
The skin is the largest organ in the human body. It is readily exposed to different kinds of damages and injuries. When the skin and its surrounding tissues are unable to redistribute external pressure and mechanical forces, ulcers may be formed. Prolonged continuous exposure to even modest pressure, such as the pressure created by the body weight of a supine patient on their posterior skin surfaces, may lead to a pressure ulcer. In the presence of other damage, such as the neuropathy and peripheral tissue weakening that can be induced by diabetes, even periodic exposure to moderate levels of pressure and stress may lead to an ulcer, for example a foot ulcer.
Pressure ulcers are developed by approximately 2.5 million people a year in the United States and an equivalent number in the European Union. In long-term and critical-care settings, up to 25% of elderly and immobile patients develop pressure ulcers. Approximately 60,000 U.S. patients die per year due to infection and other complications from pressure ulcers.
Detecting tissue damage before the skin breaks and intervening with the appropriate therapy to avoid further deterioration of the underlying tissue is desirable not only for the patient but society. The average cost of treating pressure-induced damage at the earliest visible sign (a
Stage
1 ulcer) is only $2,000 but this rises to $129,000 when the ulcer is deep enough to expose muscle or bone (a
Stage
4 ulcer.) Currently, patients normally receive universal prevention of pressure ulcers, meaning that the prevention does not target to any particular anatomical sites. Patients only receive a targeted, localized, treatment of ulcer after the pressure ulcer is developed to the point that it can be identified by a visual assessment. The current standard to detect pressure ulcers is by visual inspection, which is subjective, unreliable, untimely, and lacks specificity. Therefore, even when a patient is experiencing inflammation of the skin, a precursor of ulcer development, he or she would not be receiving a targeted, localized treatment for the developing ulcer. Instead, the inflammation would continue to develop into a full-blown ulcer.
In current practice, an independent assessment of a patient's risk of developing a pressure ulcer is performed upon arrive in a care setting. This lack of knowledge from the prior care setting may diminish the quality of care received at the new care setting.
SUMMARY
In one aspect, the present disclosure provides for, and includes, a method of identifying and providing an appropriate level of pressure ulcer care to a patient based on a plurality of Sub-Epidermal Moisture (SEM) measurements. In an aspect, a patient is provided with increasingly effective pressure ulcer interventions based on changes in SEM measurements. In an aspect, a patient is given less intensive pressure ulcer interventions based on changes in SEM measurements.
A method of providing a continuity of care for a patient during transfer between care settings, the method comprising the steps of: deciding to transfer a patient from a first care setting to a second care setting, performing a first assessment of the patient in the first care setting, preparing a transfer record of the assessment, and transferring the transfer record with the patient to the second care setting.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of pressure ulcer treatment, the method comprising the steps of: evaluating a patient for a risk of pressure ulcer in a patient upon admission to a care facility, where the evaluating step comprises making a first plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a first delta value from a portion of the first plurality of SEM measurements, determining whether the first delta value exceeds a first threshold, administering a first intervention of level-0 if the first delta value does not exceed the first threshold, and administering a first intervention of level-N if the first delta value exceeds the first threshold, where N is an integer and N has a value of 1 or greater. In a further aspect, the present disclosure provides for, and includes, making a second plurality of SEM measurements in the patient at a first pre-determined frequency corresponding to the administered intervention level, calculating a second delta value from a portion of the second plurality of SEM measurements, determining whether the second delta value exceeds a second threshold, continuing to administer the first intervention if the second delta value does not exceed the second threshold, continuing to make a plurality of SEM measurements at the first pre-determined frequency if the second delta value does not exceed the second threshold, administering a second intervention of level-M if the second delta value exceeds the second threshold, where M is an integer and M is greater than N, and making a plurality of SEM measurements at a second pre-determined frequency corresponding to level-M if the second delta value exceeds the second threshold. In yet a further aspect, the present disclosure provides for, and includes, determining whether the second delta value is less than a third threshold, administering a level-(N−1) intervention if the second delta value is less than the third threshold and if the first intervention is not of level-0, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-(N−1) if the second delta value is less than the third threshold.
In one aspect, the present disclosure provides for, and includes, a method of slowing the progression of pressure ulcer development in a patient in need thereof, the method comprising the steps of: identifying a current intervention of level-K received by the patient, making a plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a first threshold, continuing to administer the current intervention if the delta value does not exceed the first threshold, continuing to make a plurality of SEM measurements at a pre-determined frequency corresponding to level-K if the delta value does not exceed the first threshold, administering a new intervention of level-N if the delta value exceeds the first threshold, where N has a value greater than K, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-N if the delta value exceeds the first threshold. In a further aspect, the present disclosure provides for, and includes, determining whether the delta value is less than a second threshold, administering a level-L intervention if the delta value is less than the second threshold, where L has a non-negative value less than K, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-L if the delta value is less than the second threshold.
In an aspect, the present disclosure provides for, and includes, a method of stratifying groups of patients in a care facility based on pressure ulcer risk, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements in each of the patients, calculating a delta value from a portion of the plurality of SEM measurements for each of the patients, determining whether each delta value exceeds any values in a set of threshold values corresponding to N care levels and assigning a care level to each of the patients, rearranging the group of patients based on each of the patient's assigned care levels.
In one aspect, the present disclosure provides for, and includes, a method of reducing incidence of pressure ulcer in patients admitted to a care facility, the method comprising the steps of: evaluating a patient for a risk of pressure ulcer upon admission to the care facility, where the evaluating step comprises making a first plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a first delta value from a portion of the first plurality of SEM measurements, determining whether the first delta value exceeds a first threshold, administering a first intervention of level-0 if the first delta value does not exceed the first threshold, and administering a & intervention of level-N if the first delta value exceeds the first threshold, where N is an integer and N has a value of 1 or greater.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a barrier cream to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a barrier cream to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every two hours if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a neuro-muscular stimulation to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a neuro-muscular stimulation to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every hour if the delta value exceeds the threshold.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a topical cream to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a topical cream to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every half an hour if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a barrier cream to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a barrier cream to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every six hours if the delta value exceeds the threshold.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a neuro-muscular stimulation to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a neuro-muscular stimulation to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every four hours if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a topical cream to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a topical cream to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every two hours if the delta value exceeds the threshold.
BRIEF DESCRIPTION OF THE DRAWINGS
The patent or application file contains at least one drawing executed in color. Copies of this patent or patent application publication with color drawing(s) will be provided by the Office upon request and payment of the necessary fee.
Aspects of the disclosure are herein described, by way of example only, with reference to the accompanying drawings. With specific reference now to the drawings in detail, it is stressed that the particulars shown are by way of example and are for purposes of illustrative discussion of aspects of the disclosure. In this regard, the description and the drawings, considered alone and together, make apparent to those skilled in the art how aspects of the disclosure may be practiced.
FIG. 1
depicts an example of an overall process for selecting a pressure ulcer treatment based on SEM values from admission to a care facility until discharge from the care facility, in accordance with the present disclosure.
FIG. 2A
is a sample visual assessment of healthy tissue in accordance with the present disclosure.
FIG. 2B
is a plot of the averages of SEM measurements taken at each location at and around a healthy sacrum in accordance with the present disclosure.
FIG. 3A
is a sample visual assessment of damaged tissue in accordance with the present disclosure.
FIG. 3B
is a plot of the averages of SEM measurements taken at each location at and around a damaged sacrum in accordance with the present disclosure.
FIG. 4
is an illustration of a process for selecting a level of intervention and monitoring based on the amount by which a delta value derived from SEM measurements exceeds a threshold value in accordance with the present disclosure.
FIG. 5
is an example of a workflow guidance matrix where the current level of intervention and the new delta value are used to select the new level of intervention in accordance with the present disclosure.
FIGS. 6A, 6B, and 6C
depict an example progression over time of a delta value for a single patient at a single location where a pressure ulcer develops in accordance with the present disclosure.
FIG. 6D
is an example plot of a delta value change over time for a single patient at a single location where a pressure ulcer develops in accordance with the present disclosure.
FIGS. 7A and 7B
are examples of methods of mapping areas of tissue damage in accordance with the present disclosure.
FIG. 8A
is an example of a currently recommended treatment decision pathway for preventing pressure ulcers in hospital patients using a combination of risk assessment and visual assessment.
FIG. 8B
is an example of a current augmented treatment decision pathway for preventing pressure ulcers as currently implemented at some health care facilities.
FIG. 9
is an example flowchart of how a SEM Scanner may be used in a stand-alone process to prevent pressure ulcers, in accordance with the present disclosure.
FIG. 10
is an example flowchart of how a SEM Scanner may be used as an adjunct to further improve the augmented treatment decision pathway of
FIG. 8B
, in accordance with the present disclosure.
FIG. 11
illustrates the concept of providing a continuity of care across multiple care settings, in accordance with the present disclosure.
DETAILED DESCRIPTION
This description is not intended to be a detailed catalog of all the different ways in which the disclosure may be implemented, or all the features that may be added to the instant disclosure. For example, features illustrated with respect to one embodiment may be incorporated into other embodiments, and features illustrated with respect to a particular embodiment may be deleted from that embodiment. Thus, the disclosure contemplates that in some embodiments of the disclosure, any feature or combination of features set forth herein can be excluded or omitted. In addition, numerous variations and additions to the various embodiments suggested herein will be apparent to those skilled in the art in light of the instant disclosure, which do not depart from the instant disclosure. In other instances, well-known structures, interfaces, and processes have not been shown in detail in order not to unnecessarily obscure the invention. It is intended that no part of this specification be construed to effect a disavowal of any part of the full scope of the invention. Hence, the following descriptions are intended to illustrate some particular embodiments of the disclosure, and not to exhaustively specify all permutations, combinations and variations thereof.
Unless otherwise defined, all technical and scientific terms used herein have the same meaning as commonly understood by one of ordinary skill in the art to which this disclosure belongs. The terminology used in the description of the disclosure herein is for the purpose of describing particular aspects or embodiments only and is not intended to be limiting of the disclosure.
All publications, patent applications, patents and other references cited herein are incorporated by reference in their entireties for the teachings relevant to the sentence and/or paragraph in which the reference is presented. References to techniques employed herein are intended to refer to the techniques as commonly understood in the art, including variations on those techniques or substitutions of equivalent techniques that would be apparent to one of skill in the art.
U.S. patent application Ser. No. 14/827,375 (“the '375 application”) discloses an apparatus that uses radio frequency (RF) energy to measure the sub-epidermal capacitance using a bipolar sensor, where the sub-epidermal capacitance corresponds to the moisture content of the target region of skin of a patient. The '375 application also discloses an array of these bipolar sensors of various sizes.
U.S. patent application Ser. No. 15/134,110 discloses an apparatus for measuring sub-epidermal moisture (SEM) similar to the device shown in
FIG. 3
, where the device emits and receives an RF signal at a frequency of 32 kHz through a single coaxial sensor and generates a bioimpedance signal, then converts this signal to a SEM value.
Both U.S. patent application Ser. Nos. 14/827,375 and 15/134,110 are incorporated herein by reference in their entireties. However, the SEM values of this application may be measured by any similar or equivalent devices or techniques that would be apparent to one of skill in the art. For example, a device measuring the SEM values of this application may be a wired device, a wireless device, or a system comprising various components in communication with each other.
Unless the context indicates otherwise, it is specifically intended that the various features of the disclosure described herein can be used in any combination. Moreover, the present disclosure also contemplates that in some embodiments of the disclosure, any feature or combination of features set forth herein can be excluded or omitted.
The methods disclosed herein include and comprise one or more steps or actions for achieving the described method. The method steps and/or actions may be interchanged with one another without departing from the scope of the present disclosure. In other words, unless a specific order of steps or actions is required for proper operation of the embodiment, the order and/or use of specific steps and/or actions may be modified without departing from the scope of the present disclosure.
As used in the description of the disclosure and the appended claims, the singular forms “a,” “an,” and “the” are intended to include the plural forms as well, unless the context clearly indicates otherwise.
As used herein, “and/or” refers to and encompasses any and all possible combinations of one or more of the associated listed items, as well as the lack of combinations when interpreted in the alternative (“or”).
The terms “about” and “approximately” as used herein when referring to a measurable value such as a length, a frequency, or a SEM value and the like, is meant to encompass variations of ±20%, ±10%, ±5%, ±1%, ±0.5%, or even ±0.1% of the specified amount.
As used herein, phrases such as “between X and Y” and “between about X and Y” should be interpreted to include X and Y. As used herein, phrases such as “between about X and Y” mean “between about X and about Y” and phrases such as “from about X to Y” mean “from about X to about Y.”
As used herein, the term “sub-epidermal moisture” or “SEM” refers to the increase in tissue fluid and local edema caused by vascular leakiness and other changes that modify the underlying structure of the damaged tissue in the presence of continued pressure on tissue, apoptosis, necrosis, and the inflammatory process.
As used herein, a “patient” may be a human or animal subject.
As used herein, “delta” refers to a calculated difference between two SEM values.
As used herein, the variables “K,” “L,” “M,” and “N” are non-negative integers.
FIG. 1
depicts an
overall process
100
for selecting a pressure ulcer treatment based on SEM values produced from SEM measurements made using an SEM scanner in accordance with this disclosure, from admission to a care facility until discharge from the care facility. In an aspect, a care facility is selected from the group consisting of a hospital, an assisted living facility, a residential care facility, a nursing home, a long-term care facility, a continuing care community, and an independent living community. In an aspect, a care facility may be a home or other residence of the patient, whereupon the “admit”
step
102
will be a first evaluation of a patient at their home by a nurse or other caregiver. In one aspect, the schedule of interventions and evaluation intervals used in a home setting may be different than the corresponding interventions and intervals used at a hospital.
In an aspect, in
process
100
, a newly admitted patient receives an intake evaluation in
step
104
that includes one or more of a visual examination of a portion of the patient's skin, completion of at least a portion of a risk assessment protocol that evaluates one or more of nutrition, mobility, physical activity, physical strength, and ability to communicate, and SEM measurements made in one or more locations on the patient's skin. In an aspect, the SEM measurements may include making a plurality of SEM measurements at a single “location” on the patient's skin. In one aspect, “location” is considered as an area rather than a single point such that SEM measurements may be made at spatially separated points within the location. For example, a “heel” location includes the medial, lateral, and posterior surfaces around the heel as well as the posterior portion of the sole of that foot.
In one aspect, once the evaluation step is complete, a determination is made in
step
106
as to whether the patient is “deviated,” i.e., whether the combination of the results of the various elements of the evaluation indicate that the patient has, or is at risk of developing, tissue damage that could lead to a pressure ulcer. Each element of the evaluation may have an individual criterion for level of risk, for example a scoring system with threshold value that indicates an unacceptable risk. In an aspect, there is a protocol to combine the criteria to generate a composite parameter that can be used to select a level of intervention.
In an aspect, if the patient is determined to be at an acceptable level of risk, the process branches to step
108
which implements the lowest level of intervention, designated herein as “level-zero” or “level-0.” Progressing through
steps
110
and
112
, the patient will be re-assessed using at least the SEM measurement protocol in
step
114
at a frequency, or conversely a time interval, associated with level-0. The
process
100
then loops back to step
106
to evaluate the results of the SEM measurements made in
step
114
.
In one aspect, if the patient is determined in
step
106
to be deviated, then the process branches to step
122
, which implements a higher level of intervention. In an aspect, there is a defined hierarchy of intervention levels, with each level implementing a more effective intervention than the next-lower level. In an aspect, each level also has a defined monitoring interval or frequency indicating how often a set of SEM measurements should be made, where higher levels will generally have shorter intervals. In this example, the process has been defined by the hospital, or other administering organization, to step up one level to a level-1 intervention at this point. In another aspect, step
122
may implement a level-2 or higher level of intervention. The process now enters a new loop starting at
step
130
where the patient will now be monitored at a level-N frequency where N is in the range of 1 to n, n being the highest defined level of intervention and monitoring.
In an aspect, at
step
134
, the patient's history is evaluated to determine whether their condition is improving. If the patient's condition is improving, for example as evidenced by a decreasing delta value, then the process branches to step
142
. In this example,
step
142
continues to implement the current level of intervention and the process loops through
step
140
to steps
130
-
132
-
134
-
142
-
140
until the delta value drops below the threshold. In an aspect, the level of intervention may be reduced in
step
142
based on the magnitude of the delta value as the delta value trends downward.
In one aspect, if the patient does not show improvement in
step
134
, the process branches to an increase in the level of intervention in
step
138
provided that the skin is not broken, i.e., an open ulcer has not developed, in
step
136
. If an open ulcer has developed, the SEM scanning will now be performed around the periphery of the open wound in
step
144
to map inflammation or other precursor indication of the ulcer spreading. The ulcer itself is treated in
step
148
and this secondary loop
144
-
146
-
148
-
150
continues until the wound closes, whereupon the process returns to step
130
.
In an aspect, at any time in
process
100
, discharge of the patient branches to step
118
, where the condition of the patient upon discharge or transfer is documented. In an aspect,
step
118
comprises a final set of SEM measurements at one of more locations on the patient's body. In an aspect, these locations include areas that were not receiving an intervention and were not previously identified as at risk. In an aspect, this information is provided to the receiving caregiver. The patient is then discharged or transferred in
step
120
.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of pressure ulcer treatment, the method comprising the steps of: evaluating a patient for a risk of pressure ulcer in a patient upon admission to a care facility, where the evaluating step comprises making a first plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a first delta value from a portion of the first plurality of SEM measurements, determining whether the first delta value exceeds a first threshold, administering a first intervention of level-0 if the first delta value does not exceed the first threshold, and administering a first intervention of level-N if the first delta value exceeds the first threshold, where N is an integer and N has a value of 1 or greater.
In one aspect, a first plurality of SEM measurements is taken at and around one or more anatomical sites selected from the group consisting of a sternum, a sacrum, a heel, a scapula, an elbow, an ear, and other fleshy tissues of a patient. In an aspect, a first plurality of SEM measurements is separated into sub-groups for analysis based on the general location at which a measurement is taken. In one aspect, a first plurality of SEM measurements is taken at locations located on one or more concentric circles centered around an anatomical site. In an aspect, a first plurality of SEM measurements is taken at locations located on a straight line at approximately equidistance from an anatomical site.
In one aspect, a first delta value is determined by the difference between the maximum SEM value and the minimum SEM value from the first plurality of SEM measurements collected. In an aspect, a first delta value is determined by the difference between the maximum SEM average of measurements taken at one location and the minimum SEM average of measurements taken at a second location. In one aspect, a first delta value is determined for a portion of a first plurality of SEM measurements made up of a sub-group as defined by location taken. In an aspect, an average SEM value at a location is obtained from two, three, four, five, six, seven, eight, nine, ten, or more than ten SEM values measured at that location. In one aspect, a first delta value is determined by the difference between SEM values derived from measurements taken at two bisymmetric locations with respect to a centerline.
In an aspect, a delta value may be calculated from a plurality of SEM measurements made at a certain location, or in close proximity around a specific location, in a plurality of methods. In an aspect, a plurality of SEM measurements are made in a pre-determined pattern on the skin and the delta value is calculated by subtracting the SEM value associated with a pre-determined position within the pattern from the largest SEM value made at the other positions in the pattern. In an aspect, a plurality of SEM measurements are made in a pre-determined pattern on the skin and the delta value is calculated by identifying the SEM value associated with a pre-determined position within the pattern and subtracting the largest SEM value made at the other positions in the pattern. In an aspect, an average SEM value may be calculated from a portion of a set of SEM values generated by a plurality of SEM measurements at a single location and a delta value calculated as the largest difference between the average and a single SEM value of the same set. In an aspect, a delta value may be calculated as a ratio of the largest SEM value to the smallest SEM value within a set of SEM values.
In an aspect, a first threshold may be about 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, or 7.5. In one aspect, a first threshold may range from 0.1 to 8.0, such as from 0.1 to 1.0, from 1.1 to 2.0, from 2.1 to 3.0, from 3.1 to 4.0, from 4.1 to 5.0, from 5.1 to 6.0, from 6.1 to 7.0, from 7.1 to 8.0, from 0.1 to 7.5, from 0.5 to 8.0, from 1.0 to 7.0, from 1.5 to 6.5, from 2.0 to 6.0, from 3.0 to 5.5, from 3.5 to 5.0, or from 4.0 to 4.5. In an aspect, a first threshold can be scaled by a factor or a multiple based on the values provided herein. It will be understood that a threshold is not limited by design, but rather, one of ordinary skill in the art would be capable of choosing a predetermined value based on a given unit of SEM. In one aspect, thresholds of the present disclosure are varied according to the specific portion of a patient's body on which measurements are being made, or one or more characteristics of the patient such as age, height, weight, family history, ethnic group, and other physical characteristics or medical conditions.
In an aspect, N ranges from 1 to 50, such as from 1 to 2, from 1 to 3, from 1 to 4, from 1 to 5, from 1 to 6, from 1 to 7, from 1 to 8, from 1 to 9, from 1 to 10, from 1 to 15, from 1 to 20, from 1 to 25, from 1 to 30, from 1 to 35, from 1 to 40, or from 1 to 45.
In one aspect, N is determined by the amount by which the first delta value exceeds the first threshold. In an aspect, the amount by which a delta value exceeds a threshold established for (N+1) is greater than the amount by which a delta value exceeds a threshold established for N. In one aspect, the amount by which a delta value exceeds a threshold established for (N−1) is less than the amount by which a delta value exceeds a threshold established for N.
In an aspect, a level-1 (N=1) intervention is applied to a patient having a delta value exceeding the threshold by not more than 100% of the threshold value, such as not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In an aspect, a level-2 (N=2) intervention is applied to a patient having a delta value exceeding the threshold by not more than 150% of the threshold value, such as not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-3 (N=3) intervention is applied to a patient having a delta value exceeding the threshold by not more than 200% of the threshold value, such as not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-4 (N=4) intervention is applied to a patient having a delta value exceeding the threshold by not more than 250% of the threshold value, such as not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-5 (N=5) intervention is applied to a patient having a delta value exceeding the threshold by not more than 300% of the threshold value, such as not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-6 (N=6) intervention is applied to a patient having a delta value exceeding the threshold by not more than 350% of the threshold value, such as not more than 345%, not more than 340%, not more than 335%, not more than 330%, not more than 325%, not more than 320%, not more than 315%, not more than 310%, not more than 305%, not more than 300%, not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-7 (N=7) intervention is applied to a patient having a delta value exceeding the threshold by not more than 400% of the threshold value, such as not more than 395%, not more than 390%, not more than 385%, not more than 380%, not more than 375%, not more than 370%, not more than 365%, not more than 360%, not more than 355%, not more than 350%, not more than 345%, not more than 340%, not more than 335%, not more than 330%, not more than 325%, not more than 320%, not more than 315%, not more than 310%, not more than 305%, not more than 300%, not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-8 (N=8) intervention is applied to a patient having a delta value exceeding the threshold by not more than 450% of the threshold value, such as not more than 445%, not more than 440%, not more than 435%, not more than 430%, not more than 425%, not more than 420%, not more than 415%, not more than 410%, not more than 405%, not more than 400%, not more than 395%, not more than 390%, not more than 385%, not more than 380%, not more than 375%, not more than 370%, not more than 365%, not more than 360%, not more than 355%, not more than 350%, not more than 345%, not more than 340%, not more than 335%, not more than 330%, not more than 325%, not more than 320%, not more than 315%, not more than 310%, not more than 305%, not more than 300%, not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-9 (N=9) intervention is applied to a patient having a delta value exceeding the threshold by not more than 500% of the threshold value, such as not more than 495%, not more than 490%, not more than 485%, not more than 480%, not more than 475%, not more than 470%, not more than 465%, not more than 460%, not more than 455%, not more than 450%, not more than 445%, not more than 440%, not more than 435%, not more than 430%, not more than 425%, not more than 420%, not more than 415%, not more than 410%, not more than 405%, not more than 400%, not more than 395%, not more than 390%, not more than 385%, not more than 380%, not more than 375%, not more than 370%, not more than 365%, not more than 360%, not more than 355%, not more than 350%, not more than 345%, not more than 340%, not more than 335%, not more than 330%, not more than 325%, not more than 320%, not more than 315%, not more than 310%, not more than 305%, not more than 300%, not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-10 (N=10) intervention is applied to a patient having a delta value exceeding the threshold by not more than 550% of the threshold value, such as not more than 545%, not more than 540%, not more than 535%, not more than 530%, not more than 525%, not more than 520%, not more than 515%, not more than 510%, not more than 505%, not more than 500%, not more than 495%, not more than 490%, not more than 485%, not more than 480%, not more than 475%, not more than 470%, not more than 465%, not more than 460%, not more than 455%, not more than 450%, not more than 445%, not more than 440%, not more than 435%, not more than 430%, not more than 425%, not more than 420%, not more than 415%, not more than 410%, not more than 405%, not more than 400%, not more than 395%, not more than 390%, not more than 385%, not more than 380%, not more than 375%, not more than 370%, not more than 365%, not more than 360%, not more than 355%, not more than 350%, not more than 345%, not more than 340%, not more than 335%, not more than 330%, not more than 325%, not more than 320%, not more than 315%, not more than 310%, not more than 305%, not more than 300%, not more than 295%, not more than 290%, not more than 285%, not more than 280%, not more than 275%, not more than 270%, not more than 265%, not more than 260%, not more than 255%, not more than 250%, not more than 245%, not more than 240%, not more than 235%, not more than 230%, not more than 225%, not more than 220%, not more than 215%, not more than 210%, not more than 205%, not more than 200%, not more than 195%, not more than 190%, not more than 185%, not more than 180%, not more than 175%, not more than 170%, not more than 165%, not more than 160%, not more than 155%, not more than 150%, not more than 145%, not more than 140%, not more than 135%, not more than 130%, not more than 125%, not more than 120%, not more than 115%, not more than 110%, not more than 100%, not more than 95%, not more than 90%, not more than 85%, not more than 80%, not more than 75%, not more than 70%, not more than 65%, not more than 60%, not more than 55%, not more than 50%, not more than 45%, not more than 40%, not more than 35%, not more than 30%, not more than 25%, not more than 20%, not more than 15%, not more than 10%, or not more than 5% of the threshold value.
In one aspect, a level-N intervention is more effective than a level-0 intervention. In an aspect, a level-(N+1) intervention is more effective than a level-N intervention. In one aspect, a level-(N−1) intervention is less effective than a level-N intervention.
In an aspect, the evaluating step of the present disclosure further comprises performing a visual assessment. In one aspect, the visual assessment is performed in accordance with the guidelines of the National Pressure Ulcer Advisory Panel (NPUAP).
In one aspect, the evaluating step of the present disclosure further comprises performing a risk assessment. In an aspect, the risk assessment is performed in accordance with a test selected from the group consisting of the Braden Scale, the Gosnell Scale, the Norton Scale, and the Waterlow Scale.
In an aspect, the present disclosure further provides for, and includes, making a second plurality of SEM measurements in the patient at a first pre-determined frequency corresponding to the administered intervention level, calculating a second delta value from a portion of the second plurality of SEM measurements, determining whether the second delta value exceeds a second threshold, continuing to administer the first intervention if the second delta value does not exceed the second threshold, continuing to make a plurality of SEM measurements at the first pre-determined frequency if the second delta value does not exceed the second threshold, administering a second intervention of level-M if the second delta value exceeds the second threshold, where M is an integer and M is greater than N, and making a plurality of SEM measurements at a second pre-determined frequency corresponding to level-M if the second delta value exceeds the second threshold.
In one aspect, a pre-determined frequency is selected from the group consisting of at least once every 72 hours, at least once every 48 hours, at least once every 24 hours, at least once every 12 hours, at least once every 8 hours, at least once every 6 hours, at least once every 4 hours, at least once every 3 hours, at least once every 2 hours, at least once every hour, and at least once every half an hour.
In one aspect, a second plurality of SEM measurements are taken in accordance with.
In an aspect, a second plurality of SEM measurements are made at the same locations where a first plurality of SEM measurements were taken. In one aspect, a second plurality of SEM measurements are made at some of the same locations where a first plurality of SEM measurements were taken. In an aspect, a second plurality of SEM measurements are made near the locations where a first plurality of SEM measurements were taken. In one aspect, a second plurality of SEM measurements are made at different locations than where a first plurality of SEM measurements were taken.
In an aspect, a second delta value is determined by the difference between the maximum SEM value and the minimum SEM value from the second plurality of SEM measurements collected. In one aspect, a second delta value is determined by the difference between the maximum SEM average of measurements taken at one location and the minimum SEM average of measurements taken at a second location. In one aspect, a second delta value is determined for a portion of a second plurality of SEM measurements made up of a sub-group as defined by location taken.
In an aspect, a second threshold may be about 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, or 7.5. In one aspect, a second threshold may range from 0.1 to 8.0, such as from 0.1 to 1.0, from 1.1 to 2.0, from 2.1 to 3.0, from 3.1 to 4.0, from 4.1 to 5.0, from 5.1 to 6.0, from 6.1 to 7.0, from 7.1 to 8.0, from 0.1 to 7.5, from 0.5 to 8.0, from 1.0 to 7.0, from 1.5 to 6.5, from 2.0 to 6.0, from 3.0 to 5.5, from 3.5 to 5.0, or from 4.0 to 4.5. In an aspect, a second threshold can be scaled by a factor or a multiple based on the values provided herein. In one aspect, a second threshold can be the same as a first threshold. In an aspect, a second threshold can be greater than a first threshold. In one aspect, a second threshold can be less than a first threshold.
In an aspect, M ranges from 2 to 50, such as from 2 to 3, from 2 to 4, from 2 to 5, from 2 to 6, from 2 to 7, from 2 to 8, from 2 to 9, from 2 to 10, from 2 to 15, from 2 to 20, from 2 to 25, from 2 to 30, from 2 to 35, from 2 to 40, or from 2 to 45.
In one aspect, M is determined by the amount by which the second delta value exceeds the second threshold. In an aspect, the amount by which a delta value exceeds a threshold established for (M+1) is greater than the amount by which a delta value exceeds a threshold established for M. In one aspect, the amount by which a delta value exceeds a threshold established for (M−1) is less than the amount by which a delta value exceeds a threshold established for M.
In an aspect, a level M intervention is chosen in accordance with [0063] to [0072], replacing N with M.
In one aspect, the present disclosure further provides for, and includes, determining whether the second delta value is less than a third threshold, administering a level-(N−1) intervention if the second delta value is less than the third threshold and if the first intervention is not of level-0, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-(N−1) if the second delta value is less than the third threshold.
In an aspect, a third threshold may be about 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, or 7.5. In one aspect, a third threshold may range from 0.1 to 8.0, such as from 0.1 to 1.0, from 1.1 to 2.0, from 2.1 to 3.0, from 3.1 to 4.0, from 4.1 to 5.0, from 5.1 to 6.0, from 6.1 to 7.0, from 7.1 to 8.0, from 0.1 to 7.5, from 0.5 to 8.0, from 1.0 to 7.0, from 1.5 to 6.5, from 2.0 to 6.0, from 3.0 to 5.5, from 3.5 to 5.0, or from 4.0 to 4.5. In an aspect, a third threshold can be scaled by a factor or a multiple based on the values provided herein. In one aspect, a third threshold can be the same as a second threshold. In an aspect, a third threshold can be greater than a second threshold. In one aspect, a third threshold can be less than a second threshold. In one aspect, a third threshold can be the same as a first threshold. In an aspect, a third threshold can be greater than a first threshold. In one aspect, a third threshold can be less than a first threshold.
In an aspect, a second delta value can be 0.1-99.5% of the third threshold, such as 0.1-1%, 0.1-5%, 1-5%, 5-15%, 10-20%, 15-25%, 20-30%, 25-35%, 30-40%, 35-45%, 40-50%, 0.1-25%, 15-35%, 25-50%, 25-75%, 45-55%, 50-60%, 55-65%, 60-70%, 65-75%, 40-55%, 50-75%, 50-99.5%, 70-80%, 75%-85%, 80-90%, 85-95%, 90-99.5%, 65-85%, or 75-99.5% of the third threshold.
In one aspect, the present disclosure provides for, and includes, a method of slowing the progression of pressure ulcer development in a patient in need thereof, the method comprising the steps of: identifying a current intervention of level-K received by the patient, making a plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a first threshold, continuing to administer the current intervention if the delta value does not exceed the first threshold, continuing to make a plurality of SEM measurements at a pre-determined frequency corresponding to level-K if the delta value does not exceed the first threshold, administering a new intervention of level-N if the delta value exceeds the first threshold, where N has a value greater than K, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-N if the delta value exceeds the first threshold. In an aspect, a patient in need thereof is a patient experiencing a change of care, a change in mobility, a change in nutrition, a change in sensory perception, or a combination thereof. In one aspect, a patient in need thereof is a patient having developed an open ulcer. In an aspect, a patient in need thereof is a patient having recovered from an open ulcer. In one aspect, a patient in need thereof is a patient receiving surgery. In an aspect, a patient in need thereof is a patient receiving spinal analgesics or sacral analgesics during a surgery. In one aspect, a patient in need thereof is a patient receiving a surgery for a duration of four or more hours, such as five or more hours, six or more hours, seven or more hours, eight or more hours, nine or more hours, ten or more hours, eleven or more hours, or twelve or more hours. In an aspect, a surgery has a duration of one or more hours, such as two or more hours, or three or more hours.
In one aspect, a plurality of SEM measurements are taken in accordance with [
0057
]. In an aspect, a delta value is determined in accordance with [
0058
]. In one aspect, a first threshold is determined in accordance with [
0060
].
In an aspect, K ranges from 2 to 50, such as from 2 to 3, from 2 to 4, from 2 to 5, from 2 to 6, from 2 to 7, from 2 to 8, from 2 to 9, from 2 to 10, from 2 to 15, from 2 to 20, from 2 to 25, from 2 to 30, from 2 to 35, from 2 to 40, or from 2 to 45.
In an aspect, K is determined by the amount by which the delta value exceeds the threshold. In an aspect, the amount by which a delta value exceeds a threshold established for (K+1) is greater than the amount by which a delta value exceeds a threshold established for K. In one aspect, the amount by which a delta value exceeds a threshold established for (K−1) is less than the amount by which a delta value exceeds a threshold established for K.
In an aspect, a level K intervention is chosen in accordance with [0063] to [0072], replacing N with K.
In an aspect, the present disclosure further provides for, and includes, determining whether the delta value is less than a second threshold, administering a level-L intervention if the delta value is less than the second threshold, where L has a non-negative value less than K, and making a plurality of SEM measurements at a pre-determined frequency corresponding to level-L if the delta value is less than the second threshold.
In an aspect, a second threshold is determined in accordance with [0080].
In an aspect, L can be K-1, K-2, K-3, K-4, K-5, K-6, K-7, K-8, K-9, or K-10. In one aspect, L is K-1 if a delta value is 90-99.5% of the second threshold, such as 90-95%, 91-96%, 92-97%, 93-98%, 94-99%, or 95-99.5% of the second threshold, unless K-1 is less than 0, in which case L would be 0. In an aspect, L is K-2 if a delta value is 80-89.9% of the second threshold, such as 80-85%, 81-86%, 82-87%, 83-88%, 84-89%, or 85-89.9% of the second threshold, unless K-2 is less than 0, in which case L would be 0. In one aspect, L is K-3 if a delta value is 70-79.9% of the second threshold, such as 70-75%, 71-76%, 72-77%, 73-78%, 74-79%, or 75-79.9% of the second threshold, unless K-3 is less than 0, in which case L would be 0. In an aspect, L is K-4 if a delta value is 60-69.9% of the second threshold, such as 60-65%, 61-66%, 62-67%, 63-68%, 64-69%, or 65-69.9% of the second threshold, unless K-4 is less than 0, in which case L would be 0. In one aspect, L is K-5 if a delta value is 50-59.9% of the second threshold, such as 50-55%, 51-56%, 52-57%, 53-58%, 54-59%, or 55-59.9% of the second threshold, unless K-5 is less than 0, in which case L would be 0. In an aspect, L is K-6 if a delta value is 40-49.9% of the second threshold, such as 40-45%, 41-46%, 42-47%, 43-48%, 44-49%, or 45-49.9% of the second threshold, unless K-6 is less than 0, in which case L would be 0. In one aspect, L is K-7 if a delta value is 30-39.9% of the second threshold, such as 30-35%, 31-36%, 32-37%, 33-38%, 34-39%, or 35-39.9% of the second threshold, unless K-7 is less than 0, in which case L would be 0. In an aspect, L is K-8 if a delta value is 20-29.9% of the second threshold, such as 20-25%, 21-26%, 22-27%, 23-28%, 24-29%, or 25-29.9% of the second threshold, unless K-8 is less than 0, in which case L would be 0. In one aspect, L is K-9 if a delta value is 10-19.9% of the second threshold, such as 10-15%, 11-16%, 12-17%, 13-18%, 14-19%, or 15-19.9% of the second threshold, unless K-9 is less than 0, in which case L would be 0. In an aspect, L is K-10 if a delta value is 0.1-9.9% of the second threshold, such as 0.1-5%, 1-6%, 2-7%, 3-8%, 4-9%, or 5-9.9% of the second threshold, unless K-10 is less than 0, in which case L would be 0.
In an aspect, the present disclosure provides for, and includes, a method of stratifying groups of patients in a care facility based on pressure ulcer risk, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements in each of the patients, calculating a delta value from a portion of the plurality of SEM measurements for each of the patients, determining whether each delta value exceeds any values in a set of threshold values corresponding to N care levels and assigning a care level to each of the patients, rearranging the group of patients based on each of the patient's assigned care levels.
In one aspect, the present disclosure provides for, and includes, a method of reducing incidence of pressure ulcer in patients admitted to a care facility, the method comprising the steps of: evaluating a patient for a risk of pressure ulcer upon admission to the care facility, where the evaluating step comprises making a first plurality of Sub-Epidermal Moisture (SEM) measurements in the patient, calculating a first delta value from a portion of the first plurality of SEM measurements, determining whether the first delta value exceeds a first threshold, administering a first intervention of level-0 if the first delta value does not exceed the first threshold, and administering a first intervention of level-N if the first delta value exceeds the first threshold, where N is an integer and N has a value of 1 or greater. In an aspect, the incidence of ulcers in patients in the care facility is reduced to less than 1 in 100, less than 1 in 200, less than 1 in 300, less than 1 in 400, less than 1 in 500, less than 1 in 600, less than 1 in 700, less than 1 in 800, less than 1 in 900, or less than 1 in 1000.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a barrier cream to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a barrier cream to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every two hours if the delta value exceeds the threshold. In an aspect, a plurality of SEM measurements are made at least once every hour or at least once every half an hour if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a neuro-muscular stimulation to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a neuro-muscular stimulation to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every hour if the delta value exceeds the threshold. In an aspect, a plurality of SEM measurements are made at least once every half an hour if the delta value exceeds the threshold.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a topical cream to the patient's heel, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's heel, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a topical cream to the patient's heel if the delta value exceeds the threshold, and making a plurality of SEM measurements every half an hour if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a barrier cream to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a barrier cream to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every six hours if the delta value exceeds the threshold. In an aspect, a plurality of SEM measurements are made at least once every four hours, at least once every three hours, at least once every two hours, at least once an hour, or at least once every half an hour if the delta value exceeds the threshold.
In an aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a neuro-muscular stimulation to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a neuro-muscular stimulation to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every four hours if the delta value exceeds the threshold. In an aspect, a plurality of SEM measurements are made at least once every three hours, at least once every two hours, at least once an hour, or at least once every half an hour if the delta value exceeds the threshold.
In one aspect, the present disclosure provides for, and includes, a method of identifying and treating a patient in need of application of a topical cream to the patient's sacrum, the method comprising the steps of: making a plurality of Sub-Epidermal Moisture (SEM) measurements at the patient's sacrum, calculating a delta value from a portion of the plurality of SEM measurements, determining whether the delta value exceeds a threshold corresponding to level N, where N is greater than or equal to 2, administering a topical cream to the patient's sacrum if the delta value exceeds the threshold, and making a plurality of SEM measurements every two hours if the delta value exceeds the threshold. In an aspect, a plurality of SEM measurements are made at least once an hour or at least once every half an hour if the delta value exceeds the threshold.
In an aspect, methods of the present disclosure are performed using the devices disclosed in U.S. application Ser. Nos. 14/827,375 and 15/134,110. In one aspect, the moisture content is equivalent to the SEM value on a predetermined scale. In an aspect, a predetermined scale may range from 0 to 20, such as from 0 to 1, from 0 to 2, from 0 to 3, from 0 to 4, from 0 to 5, from 0 to 6, from 0 to 7, from 0 to 8, from 0 to 9, from 0 to 10, from 0 to 11, from 0 to 12, from 0 to 13, from 0 to 14, from 0 to 15, from 0 to 16, from 0 to 17, from 0 to 18, from 0 to 19. In one aspect, a predetermined scale can be scaled by a factor or a multiple based on the values provided herein.
In an aspect, the present disclosure further provides for, and includes, providing targeted treatment to an anatomical location of a patient identified as being damaged by a combination of a visual assessment and SEM scan measurements. In one aspect, a targeted treatment is provided to a common site for pressure ulcers selected from the group consisting of: toes, heels, a sacrum, a spine, an elbows, shoulder blades, occiput, and ischial tuberosity. In an aspect, a targeted treatment is concurrently provided to a second common site for pressure ulcers selected from the group consisting of: toes, heels, a sacrum, a spine, an elbows, shoulder blades, occiput, and ischial tuberosity. In one aspect, a first site receiving a targeted treatment is known to cause a development of pressure ulcer at a second site.
The present disclosure is illustrated by the following examples. The examples set out herein illustrate several aspects of the present disclosure but should not be construed as limiting the scope of the present disclosure in any manner.
EXAMPLES
Example 1: Intervention Levels for Treating Pressure Ulcers in the Heel
Subjects identified as being at risk for pressure ulcers in the heel were treated in accordance with the following scheme:
TABLE 1
EXAMPLE INTERVENTION SCHEME FOR
TREATING PRESSURE ULCER IN THE HEEL
Frequency of Subsequent
Corresponding
Risk
SEM Measurement
SEM delta
Level
Intervention
Monitoring
Ranges
0
provide good nutrition, standard
every 24 hours
SEM delta ≤
mattress, and/or turn every 24
hours
threshold
1
provide a heel boot
every 10 hours
threshold <
SEM delta ≤
105
% threshold
2
change of support surface
at the beginning of each
105% threshold <
nursing shift
SEM delta ≤
110
% threshold
3
apply dressing to back or sides of
every 12
hours
110% threshold <
heel
SEM delta ≤
115
% threshold
4
change to low-friction sheet cover
every 8 hours
115% threshold <
SEM delta ≤
120
% threshold
5
provide a low-friction padded
every 6
hours
120% threshold <
mattress surface for lower leg
SEM delta ≤
125
% threshold
6
turn patient at a shorter interval
every 4 hours
125% threshold <
SEM delta ≤
130
% threshold
7
apply barrier cream
every 2
hours
130% threshold <
SEM delta ≤
135
% threshold
8
apply neuro-muscular stimulation
every 1 hour
135% threshold <
SEM delta ≤
145
% threshold
9
apply topical cream to enhance
every 30 minutes
145% threshold <
perfusion
SEM delta ≤
150% threshold
10
provide silicone pad for lower leg
every 15
minutes
150% threshold <
SEM delta
Example 2: Intervention Levels for Treating Pressure Ulcers in the Sacrum
Subjects identified as being at risk for pressure ulcers in the sacrum were treated in accordance with the following scheme:
TABLE 2
EXAMPLE INTERVENTION SCHEME FOR
TREATING PRESSURE ULCER IN THE SACRUM
Frequency of Subsequent
Corresponding
Risk
SEM Measurement
SEM delta
Level
Intervention
Monitoring
Ranges
0
provide good nutrition, standard
every 24 hours
SEM delta ≤
mattress, and/or turn every 24
hours
threshold
1
reposition patient with wedge and/or
every 10 hours
threshold <
keep sacrum dry
SEM delta ≤
110
% threshold
2
change mattress to pressure-
at the beginning of each
110% threshold <
alleviating mattresses
nursing shift
SEM delta ≤
120
% threshold
3
apply dressing over sacrum
every 12
hours
120% threshold <
SEM delta ≤
130
% threshold
4
change to dynamic mattress
every 8
hours
130% threshold <
SEM delta ≤
140
% threshold
5
apply barrier cream
every 6
hours
140% threshold <
SEM delta ≤
150
% threshold
6
apply neuro-muscular stimulation
every 4
hours
150% threshold <
SEM delta ≤
160
% threshold
7
apply topical cream to enhance
every 2 hours
160% threshold <
perfusion
SEM delta ≤
170
% threshold
8
provide silicone pad under the
every 1 hour
170% threshold <
patient's body
SEM delta ≤
180% threshold
Example 3: Identifying a Patient in Need of a Level-0 Intervention at Sacrum
A patient was subjected to multiple SEM measurements at and around the boney prominence of the sacrum using an apparatus capable of measuring SEM measurements. Prior to performing the measurements, surface moisture and matter above the patient's skin surface were removed. An electrode of the apparatus was applied to the patient's skin with sufficient pressure to ensure complete contact for approximately one second to obtain each SEM measurement.
SEM measurements were taken on a straight line across the sacrum of a patient. Multiple measurements were taken at a given measurement location.
FIG. 2A
is a sample visual assessment of healthy tissue.
FIG. 2B
is a corresponding plot of the averages of SEM measurements taken at each location. A threshold of 0.5 was chosen. A delta value was calculated as the difference between the maximum average SEM value and the minimum average SEM value, which was determined to be less than 0.5. Because the SEM delta value was below the threshold value, the patient was identified to be in need of a level-0 intervention. Accordingly, the patient was placed on a standard mattress, and was turned every 24 hours.
Additional SEM measurements were taken every 24 hours until discharge. There was no change in the intervention level.
Example 4: Identifying a Patient in Need of a Level-n Intervention at Sacrum
A patient was subjected to multiple SEM measurements taken on a straight line across the sacrum in accordance with the same procedure as described in Example 3.
FIG. 3A
is a sample visual assessment of damaged tissue.
FIG. 3B
is a corresponding plot of the averages of SEM measurements taken at each location. A threshold of 0.5 was chosen. A delta value was calculated as the difference between the maximum average SEM value and the minimum average SEM value, which was determined to be above 0.5. Because the SEM delta value was more than 200% over the threshold value, the patient was identified to be in need of a level-8 intervention. Accordingly, the patient was placed on a silicone pad and monitored on an hourly basis until a SEM delta value of less than 170% of the threshold value was observed, at which point, the patient was switched to a level-7 intervention.
Example 5: Example Process for Selecting a Level of Intervention and Monitoring
FIG. 4
is an illustration of a
process
400
for selecting a level of intervention and monitoring based on the amount by which a delta value derived from SEM measurements exceeds a threshold value. Here, a caregiver took a plurality of SEM measurements at a location on the skin of a patient using a SEM Scanner in
step
402
, where each measurement generated a SEM value. Using a portion of these SEM values, a delta value “a” was calculated in
step
404
. The delta value was calculated by subtracting the smallest SEM value from the largest SEM value generated from the plurality of SEM measurements.
The calculated delta value was compared to a threshold value “T” in
step
406
. If the delta value was less than or equal to the threshold value,
step
408
was executed and the caregiver waited until the monitoring interval associated with the current level of care transpires, then repeated the SEM measurements in
step
402
. If the delta value was greater than the threshold value, the amount by which the delta value exceeded the threshold value was compared to a cascading series of difference values.
In some instances, the delta value was positive and the comparison executed by subtracting the threshold value from the delta value, which produced a positive difference, and then a determination was made regarding whether the difference exceeded the first difference D1 in
step
410
. If the difference was less than D1, the process branched to step
412
and then step
414
to implement an intervention and measurement interval, respectively, associated with level-
N+
1. In this example, N had a value of zero or greater.
In some instances, the delta value was negative, for example if the SEM measurement at the center position of the data in
FIG. 3B
is subtracted from an average of the SEM values from the leftmost and rightmost locations in
FIG. 3B
. In that case, the differences D1, D2 through Dn was selected to have negative values that could have different absolute values than the corresponding difference values D1, D2 through Dn used for a positive delta value. Alternatively, the comparisons in
steps
410
,
420
, and
430
were changed to “≤” in place of the “≥” shown in
FIG. 4
.
Example 6: Workflow Guidance Matrix
FIG. 5
is an example of a
workflow guidance matrix
500
where the current level of
intervention
502
and the
new delta value
504
are used to select the new level of
intervention
506
. Here, a caregiver monitored the condition of a patient by periodically taking a plurality of SEM measurements at one or more locations on the patient's skin. At the time of these measurements, the patient received care associated with a level of intervention and monitoring. In this example, level-0 (zero) was associated with a patient who was not considered to be at significant risk for development of a pressure ulcer. Higher levels of intervention and monitoring were identified with the gradations of intervention ranked, for example, according to cost, difficulty to implement, or other parameter identified by the care facility. When a caregiver was making a new set of SEM measurements, they consulted this matrix by identifying the row of the current level of
intervention
502
, the delta value determined from the latest set of
SEM measurements
504
, and identified the level of intervention in the
cell
506
at the intersection of the
row
502
and
column
504
. The caregiver could consider the identified level of intervention as well as the current level of intervention and the value of the delta in selecting a level of intervention for the next time period.
In some instances, the values of the new levels of intervention in the
cells
506
were similar from row to row. In some instances, the values of the new levels of intervention in
adjacent cells
506
differed by a single level or by more than one level. In some instances, the values of the new levels of intervention in
adjacent cells
506
were the same in adjacent cells.
Example 7: Progression of Tissue Condition Leading to Pressure Ulcer
FIGS. 6A, 6B, and 6C
depict an illustrative non-limiting example of a progression over time of the tissue condition leading to a pressure ulcer.
FIG. 6A
depicts a cross-section of
healthy tissue
600
, including the
stratum corneum
602
and
healthy cells
604
in the epidermis/dermis. The
center electrode
606
and the
toroidal electrode
608
of a SEM scanner are shown in cross-section in contact with the
stratum corneum
602
. An illustrative indication of the sensitive region of the SEM Scanner is shown as the
oval region
610
. The
region
610
has a depth of sensitivity. In some instances, the depth of sensitivity is in the range of 0.14 0.16 inches. In some instances, the depth of sensitivity is less than 0.16 inches.
FIG. 6B
is an illustrative cross-section of slightly damaged
tissue
620
. Cellular damage, for example resulting from long-term application of low-level pressure has affected the tissue. Without being limited by theory, some of the
cells
622
have ruptured, releasing the fluid contents into an
intercellular space
624
. Alternatively, and without being limited by theory, an inflammatory reaction has caused fluid to migrate into the
intercellular space
624
. This damage is not visible on the skin surface.
FIG. 6C
is an
illustrative cross-section
640
of a more advanced level of damage. Without being limited by theory, the tissue is now mostly ruptured
cells
622
, which can provide little mechanical structure to carry the continued applied pressure. The tissue thickness is reduced, with the
bone
642
now closer to the skin surface. The ruptured
cells
622
and
intercellular space
624
are compressed, expelling the fluid
644
out of the local tissue as indicated by
arrows
646
.
FIG. 6D
shows an illustrative plot
660
of a delta value for a single patient at a single location where a pressure ulcer develops. The SEM values were measured by a SEM scanner. A delta value was generated from sets of SEM measurements taken at incremental times.
Point
672
was a measurement at time=zero where all the SEM values had a baseline value associated with healthy tissue and the delta value is zero. At time t
1
, another set of SEM measurements was made and the associated delta value was indicated at
point
674
. This delta value was below the
threshold
662
and, therefore, there was no indication of significant subsurface damage.
At time t
2
, the damage progressed and the
delta value
676
was greater than the
threshold
662
, indicating that there was significant damage. This damage was still not visible on the skin. Nonetheless, a delta value greater than the
threshold
662
indicated that there was cellular damage at a depth less than the sensitive depth of the SEM scanner.
At time t
3
, the damage continued but the amount of fluid in the intercellular space was decreased due to mechanical expulsion as illustrated in
FIG. 6C
. This reduced the SEM value taken over the damaged area, which reduced the computed
delta value
678
since the SEM value of the healthy tissue remained much the same as during previous measurements.
At time t
4
, the damage progressed to the point where it was visible on the skin surface, as shown in
FIG. 3A
. In some instances, time t
4
may occur before one or both of t
2
and t
3
. In some instances, time t
4
may occur after the delta value has reached zero again along
curve
670
after time t
3
and before t
5
.
Arrow
665
indicates that after time t
4
, the damage remained visible. In some instances, the tissue may be considered to be a “
stage
1” pressure ulcer after time t
4
.
At time t
5
, the damage progressed to the point where sufficient fluid had been expelled from the local tissue that the SEM value of a measurement made over the damaged area was lower than the SEM value of healthy tissue. This resulted in the
delta value
680
being negative, as shown in
FIG. 3B
. In some instances, the negative delta would indicate that the tissue is seriously damaged. In some instances, the negative delta would indicate that a portion of the tissue at the location of the lowest SEM value is necrotic.
Example 8: Method of Mapping an Area of Possible Damage I
FIG. 7A
is an example of a method of mapping an area of possible damage. The area of
damage
700
was surrounded by
healthy tissue
708
. The
center area
730
was significantly damaged. The first surrounding
area
720
was less damaged, and the second surrounding
area
710
was less damaged but still not healthy tissue. The skin over all of these areas had the same appearance and texture, with no indication of the subsurface damage. The series of dashed-line circles
740
,
742
,
744
,
746
,
748
, and
750
indicate an example set of location where SEM measurements were taken. SEM measurements taken at
locations
740
,
742
, and
750
generally produced a SEM value associated with healthy tissue, identified within this example as “H.” SEM measurements taken at
locations
744
and
748
generally produced a SEM value “J” that is slightly higher than H. A SEM measurement taken at
location
746
generally produced a SEM value “P” that is greater than J. All of these measurements were considered to be taken at a single “location” on the patient's body, for example the sacrum, even though the individual locations were spatially dispersed over this location. For this set of SEM values, the delta was the difference between the highest SEM value, which likely occurred at
location
746
, and the lowest SEM value, which likely occurred at one of
locations
740
,
742
, and
750
, within this set. If the delta was greater than a threshold value “T,” this was an indication that there is significant damage at this location. The exact location of the greatest damage was likely to be proximate to the
measurement location
746
where the greatest SEM value was produced.
Example 9: Method of Mapping an Area of Possible Damage II
FIG. 7B
depicts a second example of mapping an area of possible damage. In this example, the approximate location of the greatest damage was known, for example from prior application of the method illustrated in
FIG. 7A
. The intent of this method was to map the boundary between
area
710
and
area
720
to determine the extent of the damage. For simplicity, the SEM values produced by measurements in each area were the same and the SEM values increased from
area
710
to
area
720
and then to
area
730
. The first SEM measurement was taken at
location
760
, which was known to be the approximate location of the greatest damage. Subsequent measurements were taken at
locations
762
,
764
,
766
, and
768
in the order indicated by
path
780
. The SEM value produced at
location
764
was slightly higher than the SEM values produced at
locations
762
and
766
, indicating that
location
764
was partially within the
area
720
while
locations
762
and
766
were fully within the lesser-damaged
area
710
. The boundary could be approximated by interpolating between the various measurement locations. For example, the SEM value produced at
location
770
was high enough to suggest that it is fully within the
area
720
and therefore did not help identify the boundary between
areas
710
and
720
. The
subsequent location
772
was therefore directly away from the starting
location
760
. As
location
760
, in this example, was now fully within
area
710
, the boundary between
areas
710
and
720
could be interpolated to be between
locations
770
and
772
. The SEM value produced from a measurement at
location
774
was similar to the SEM value from
location
770
and it could be sufficient to identify the boundary as outside the
location
774
without taking another measurement at a location corresponding to
location
772
.
This set of measurements enabled the creation of a map of a certain level of damage, for example the
area
720
. Repeating this mapping process at regular time intervals would provide an indication of whether the
area
720
is growing, which may indicate that an increased level of intervention is appropriate, or shrinking, which may indicate that the current level of intervention is allowing the damage to heal.
Example 10: Treatment Decision Pathway for Stratifying Patients and Providing Appropriate Treatments
FIG. 8A
outlines a currently recommended treatment decision pathway for preventing pressure ulcers in hospital patients as presented by The National Institute for Health and Care Excellence (NICE) in their clinical guideline
Pressure ulcers: prevention and management
, published 23 Apr. 2014. The guidelines recommend that a risk analysis be performed for every patient admitted to a care facility that exhibits one or more risk factors such as significantly limited mobility, a significant loss of sensation, a previous or current pressure ulcer, a nutritional deficiency, an inability to reposition themselves, or a significant cognitive impairment. Risk assessment is commonly done using a scored checklist, such as the Braden Scale, that assesses the severity of specific risk factors.
Upon completion of the risk assessment, the patient is identified as (i) having a low risk of developing a pressure ulcer, (ii) being at risk of developing a pressure ulcer, or (iii) being at high risk of developing a pressure ulcer. Depending on the level of risk the patient is classified as having, the patient undergoes different sequences of treatment and evaluation by visual assessment.
All patients are potentially at risk of developing a pressure ulcer. They are more likely to occur in people who are seriously ill or have a neurological condition, impaired mobility, impaired nutrition, poor posture, or a deformity.
Pressure ulcers are categorized as stage-1 through stage-4, with stage-1 being the lowest condition. The National Pressure Ulcer Advisory Panel (NPUAP) has defined a “stage-1” ulcer as intact skin with a localized area of non-blanchable erythema, where “blanchable” indicates that the tissue loses all redness when pressed and “non-blanchable” tissue remains red when pressed due to the presence of red blood cells outside of blood vessels (extravasation). In some patients, blanchable erythema or changes in sensation, temperature, or firmness may precede visual changes.
Visual skin assessment (VSA) is the current method of identifying a pressure ulcer. A trained healthcare professional assesses the appearance of the skin, visually and tactilely, looking for redness or variations in tissue firmness, tissue temperature, or moisture.
If a patient is identified as having a low risk of developing a pressure ulcer, the patient is simply monitored for a change in clinical status such as undergoing surgery, worsening of an underlying condition, or a change in mobility. A patient who uses a wheelchair or sits for prolonged periods may be provided with a high-specification foam cushion or equivalent pressure-distributing cushion. If there is no change in clinical status, a low-risk patient will not be reassessed under this set of guidelines and stays within the same treatment and evaluation pathway until he or she is discharged from the care facility.
If a patient is identified as being at risk of developing a pressure ulcer, the patient will be scheduled to be turned, or “rounded,” every 6 hours. As with the low-risk patient, a high-spec foam cushion may be provided if the patient uses a wheelchair or sits for prolonged periods of time. No other monitoring or intervention is recommended by the NICE guidelines.
A high-risk patient receives a high-spec foam mattress as a preventative measure, provided with a high-spec cushion if they are in a wheelchair or sit for prolonged periods of time, and will be turned every 4 hours. The patient will receive a daily VSA for all areas of the body. If an area is found to have non-blanchable erythema, an appropriate intervention will be implemented and that area re-checked by VSA every 2 hours. Areas that do not exhibit non-blanchable erythema are re-checked daily by VSA. A personalized care plan will be developed for each high-risk patient.
It can be seen from this flow chart that the majority of the time spent by caregivers will be on the high-risk patients. While this may be appropriate, it leaves the at-risk patients unmonitored and they may develop a stage-1 ulcer before the condition is observed by a caregiver. Furthermore, the consequence of relying on VSA to detect a problem necessarily means that patients will develop a stage-1 ulcer before an intervention is selected or implemented. By the time that the damage has progressed to stage-1, it is likely that the skin will break and become a stage-2 ulcer despite intervention. There is a clear need to identify tissue damage earlier so that interventions can prevent progression of the subepidermal damage to stage-1 and beyond.
FIG. 8B
is an example of a current augmented treatment decision pathway for preventing pressure ulcers as currently implemented at some health care facilities. The augmented pathway adds monitoring steps to both the at-risk and the low-risk paths. A low-risk patient received a weekly risk assessment, for example completion of the Braden Scale assessment. A patient identified as at-risk in the initial assessment will receive a high-spec foam mattress as a preventative measure and will be evaluated daily by VSA. A care plan will be developed for the monitoring and treatment of the at-risk patient. No change is made in the care if a high-risk patient.
The augmented plan has the benefit of providing basic monitoring of all patients for pressure ulcers. The additional steps require additional time, however, either by adding staff or further burdening the existing staff. While superior to the recommended care pathway of
FIG. 8A
, the care pathway of
FIG. 8B
requires more resources and still suffers from the limitation that a patient must develop a stage-1 ulcer before VSA identifies the damage.
Various hospitals and care facilities use different numbers of risk categories, ranging from two categories, low-risk and at-risk, to four or more categories, adding categories such as “very-high-risk” to the categories of the example of
FIG. 8B
. Patients are assigned to the various categories based on the results of the initial risk assessment.
FIG. 9
is an example flowchart of how a SEM Scanner may be used in a stand-alone process to prevent pressure ulcers, in accordance with the present disclosure. Every incoming patient receives a complete SEM scanner assessment of all body locations that are selected for monitoring. These selected locations may include areas recommended in the Instructions For Use (IFU) of the SEM scanner, such as the sacrum and the heels. Additional locations may be identified by the hospital and integrated into their in-house practice. Multiple SEM measurements are taken at and around each body location at positions that are separated from each other, although this is generally referred to as taking multiple measurements at the body location. The SEM scanner calculates a “delta” value for each location from the set of measurements taken at and around that location. The delta value is then compared to one or more threshold values to categorize a patient. In this example, the patient is assigned to one of two risk categories: low-risk and at-risk.
In an aspect, the clinician will perform an SEM scan of a body location identified as having possible damage in the initial SEM scan at a first time interval. The clinician will also perform an SEM scan of all other body locations selected for monitoring at a second time interval that is longer than the first time interval. In an aspect, the values of the first and second time intervals are different depending on the risk category to which the patient has been assigned. For example, a high-risk patient will have a first time interval of 4 hours and a second time interval of 1 day while an at-risk patient will have a first time interval of 1 day and a second time interval of 1 week. In an aspect, the time interval may be event-based, for example upon a change of attending staff or shift change, rather than strictly based on time. In general, body locations that have elevated delta values are scanned more often than other body locations that are monitored but having normal delta values in previous SEM scans.
In an aspect, the interval at which an SEM scan is performed is determined by the delta values from the prior SEM scan. For example, an SEM scan of a body location that had a delta value greater than or equal to a first threshold in a previous SEM scan is performed at a first time interval, while an SEM scan is performed at a second time interval that is shorter than the first time interval when the prior SEM scan of a body location had a delta value greater than or equal to a second threshold that is higher than the first threshold.
In this example, low-risk patients receive a weekly SEM scan of all body locations that are selected for monitoring. This is a small effort that provides basic protection for even the healthiest patients, as a weekly SEM scan is likely to detect tissue damage before it becomes visible to VSA.
At-risk patients, which will include patients that would be identified as high-risk in the current care pathways of
FIGS. 8A and 8B
, will receive specialized care based on the body location that exhibits a delta value above a threshold. For example, if the sacrum body location has a delta value above a threshold, the patient will be repositioned every 6 hours and receive a SEM scan of the sacrum every day and an SEM scan of the other body locations every week.
FIG. 10
is an example flowchart of how a SEM Scanner may be used as an adjunct to further improve the augmented treatment decision pathway of
FIG. 8B
, in accordance with the present disclosure. An incoming patient receives both a risk assessment and an SEM scan of all body locations identified by the hospital for monitoring and the assignment of a patient to a risk category is based partially on the risk assessment and partially on the SEM scan results. An initial delta value that is greater than a threshold is an indication that there is possible damage at that body location. In an aspect, the assignment is based solely on the largest initial delta value found during the initial SEM scan.
A decision whether to implement an intervention, for example turning the patient at a first interval, is currently based on the VSA and risk assessment despite the uncertainty of whether there is early stage damage below the skin. In an aspect, the decision to implement an intervention for a particular body site, or a general intervention such as a high-spec mattress, is based on the delta value found for that site in the SEM scan. If the delta value is less than a predetermined threshold, no intervention is required. If the delta value is greater than the predetermined threshold, then an intervention is selected and implemented based partially on the body location and partially on the delta value for that body location. The predetermined threshold for whether or not to select and implement an intervention may be higher or lower than the threshold for determination that there is possible damage at the body location.
A comparison of the costs of provided the care pathways of
FIGS. 8A, 8B, 9, and 10
reveals one of the benefits of utilizing the SEM scanner to monitor patients. Note that the costs cited herein are for patients who do not have or develop pressure ulcers, in which case the estimated treatment cost jumps to $2000 for a stage-1 ulcer.
The baseline for this comparison is the augmented current practice of
FIG. 8B
, which represents a current “best practice” for hospitals striving to reduce the incidence rate of pressure ulcers. Providing the care of the low-risk care pathway is expected to cost an average of $26 per patient for the average hospital stay of 5.6 days, the care for an at-risk patient is estimated to cost an average of $121, and a high-risk patient is expected to cost $165. All of the care pathways rely on a VSA to detect a pressure ulcer and are otherwise implementing interventions based on “typical” patient progression rather than the particular patient's condition.
Integrating the SEM scanner into the current “best practice” workflow, as shown in
FIG. 10
, does not lower the cost of any of the care pathways as no work element is being eliminated. The benefit is in the ability to detect tissue damage at an earlier stage at a minimal incremental cost. The incremental cost of adding a SEM scan to the no-risk care pathway is $2, raising the cost from approximately $26 to $28. The expected cost of caring for an at-risk patient who does not have an elevated SEM scan delta value, i.e. does not have subepidermal tissue damage, is also increased by only $2. If an at-risk patient is found to have an elevated SEM scan delta value, however, the patient is escalated to the high-risk category, where the expected cost of care increases from $165 to $169. While this may seem like an additional cost at first glance, it represents an increase in the level of protection provided to at-risk patients.
FIG. 9
represents an example workflow that relies solely on an SEM scanner to monitor patients and forgoes the routine VSA. The expected cost of preventative care for a low-risk patient is $4, compared to the $28 cost for the integrated low-risk care pathway of
FIG. 10
. For an at-risk patient, which is the only other category for the SEM scanner care pathway of
FIG. 9
, the expected cost is $97, compared to the $123-$169 costs for the at-risk and high-risk patients of the integrated care pathway of
FIG. 10
.
FIG. 11
illustrates the concept of providing a continuity of care across multiple care settings, in accordance with the present disclosure. This example shows a
care pathway
1100
for a patient being sequentially cared for in a plurality of care settings, starting from a
home care setting
1110
. A decision is made to transfer the patient to a
hospital
1150
where the patient is initially admitted to a medical/surgical (med/surg)
unit
1120
. After receiving care in the med/
surg unit
1120
for some time, the patient is transferred to a long-
term care unit
1130
within the
same hospital
1150
. After further treatment, the patient is discharged from the
hospital
1150
to a
skilled nursing facility
1140
. Although not shown in
FIG. 11
,
care pathway
1100
is not limited to this sample sequence and combination of care settings. For example,
care pathway
1100
may also involve a discharge of a patient back to the home care setting.
In an aspect, a central “registry” or
database
1160
is established to aggregate data from all care settings as well as the condition of the patient at the time of transfer between care settings.
While in each care setting, for example the home care setting
1120
, health information regarding the patient is recorded and transferred to the
database
1160
in a
data record
1112
. The health information may include the results of examinations or tests, observations, measurements, treatments, the implementation of interventions that are intended to prevent the development of pressure ulcers, dietary notations, and other records related to the condition and treatment of the patient. A data record from a care setting may include one or more of a patient identifier, a data element from the group of nutritional information, an implemented intervention, a risk assessment, a visual skin assessment, a care plan, a doctor's note, lean event, a vital sign, a “measure of health” such as skin redness or an indication of mobility or a measure of cognition, a body weight, and a lab result, and a date/time associated with the data element. Data records may vary in structure and content. A data record reported to the database may contain one of more of the following data elements:
a) a patient identifier
b) a transaction date
c) a facility identifier
d) a location of the transaction
e) nutritional information
f) an implemented intervention
g) a risk assessment
h) a visual skin assessment
i) a care plan
j) a doctor's note (diagnosis, order, prescription, request for test, procedure, treatment, etc.)
k) results of a test, procedure, or treatment
l) an event
m) a vital sign
n) a body weight
o) a lab result
When a patient is transferred between care setting, for example from the home care setting
1110
to the med/surg care setting
1120
, a
transfer record
1114
is created and reported to the
database
1160
. Transferring information regarding risk and health information related to pressure ulcers will improve the care provided in the new care setting. In an aspect, the
transfer record
1114
comprises a patient assessment performed at the “from” care site after the decision to transfer the patient has been made. In an aspect, the assessment comprises an SEM scan of at least one body location, wherein the SEM scan comprises a plurality of SEM values measured at a single body location and calculation of a delta value from the plurality of SEM values. In an aspect, the transfer record contains a history of prior SEM values and/or delta values while in the “from” care setting. In an aspect, the transfer record contains one or more of a VSA, a risk analysis, and other health data. A transfer record may contain one of more of the following data elements:
a) a patient identifier
b) a transaction date/time (date and time, time zone or Greenwich Mean Time)
c) a transaction type (pre-admit, admit, transfer, discharge, etc.)
d) a “To” Location
e) a “From” Location
f) a facility/unit identifier
g) a risk assessment
h) a visual skin assessment
i) a photograph of a body location
A patient may move periodically from a primary care setting, for example a home care setting
1110
, to an advanced care setting, for example a long-term
acute care unit
1130
, where the patient will undergo an “episode of care” by doctors or other skilled professionals. Data records of the assessments and care provided in the advanced care setting are reported to the
database
1160
. Upon discharge from the long-term acute care setting
1130
to the
home setting
1110
, data records containing care instructions, prescriptions, and other guidance for care in the
home setting
1110
.
With data from the
entire care pathway
1100
aggregated in the
database
1160
, it is possible to query the
database
1160
to retrieve the delta values observed over time for a particular patient across multiple care settings and various episodes of care.
In an aspect, a query is structured to determine whether instructions from monitoring and/or treatment of a patient are being followed.
In an aspect, a query is structured to determine whether a treatment of a patient is effective.
In an aspect, a query is structured to determine whether an outcome of a patient is related to one or more of the data elements reported to the
database
1160
.
In an aspect, a query is structured to retrieve one or more measures of health along with delta values to evaluate possible linkages between the retrieved measures of health and the development of a pressure ulcer or other outcomes (development of other health con. The delta values are plotted against the date/time of measurement to form a time history of the delta values for a body location. In an aspect, the dealt values are analyzed to determine one or more of a slope, an acceleration, a curve shape and associated characteristics, and a time-to-intercept of a selected threshold value. In an aspect, these analytical results can be used to implement the methods and processes of
FIGS. 1 and 4
.
From the foregoing, it will be appreciated that the present disclosure can be embodied in various ways, which include but are not limited to the following:
While the present disclosure has been described with reference to particular aspects, it will be understood by those skilled in the art that various changes may be made and equivalents may be substituted for elements thereof without departing from the scope of the disclosure. In addition, many modifications may be made to a particular situation or material to the teachings of the disclosure without departing from the scope of the disclosure. Therefore, it is intended that the disclosure not be limited to the particular aspects disclosed but that the disclosure will include all aspects falling within the scope and spirit of the appended claims.
