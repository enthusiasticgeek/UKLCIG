# UKLCIG
 UnOfficial KiCAD Library Component IC Generator (UKLCIG) 

# UKLCIG
![alt text](https://github.com/enthusiasticgeek/UKLCIG/blob/master/UKLCIG.png "UKLCIG")
# UnOfficial KiCAD Library Component (PCB) IC Generator

This is a simple python based tool to generate IC Library Component PCB library files for KiCAD EDA http://kicad-pcb.org/.

#### A. Dependencies:

**Python 2.7, GTK+ 3.0, LibCairo**

#### B. Installation (Tested on Ubuntu 16.04 LTS):

**__Note:__** Replace **apt** with **apt-get** for older versions of Ubuntu in the following text.

1. Test for Python 2.7+ (usually installed) or install using **sudo apt install libpython2.7\***
2. Test for GTK-3.0+ or install the packages using **sudo apt install libgtk3\*** 
3. Test for Cairo or install the packages using **sudo apt install libcairo\***

#### C. Usage:

1. Download **uklcig.py** and cd to Download folder **chmod a+x uklcig.py** and run **./uklcig.py** and select the IC Library Component parameters (one would need the datasheet for a given component IC).

2. Enter the **IC name** (without spaces).

3. Enter the **IC Dimensions (WxL)** (width followed by length).

4. Enter the **Distance Between Pins**.

5. Enter the **Pin Width**.

6. After completion of steps 1 - 5, click **Update IC Dimensions** button.

7. (a) Right click any IC boundary unit marker. 
   (b) Right click and select **'AddPin'**. 
   (c) Double Click on this newly added pin.
   (d) Select signal and pin attributes.
   **Note:** Steps 8 - 13 pertain to this selected pin.

8. Enter the **Signal Name** and **Signal Text Size**.

9. Enter the **Pin Name** and **Pin Text Size**.

10. Select the Pin **Type** from the combobox. Refer https://www.compuphase.com/electronics/LibraryFileFormats.pdf for more information.

11. Select the Pin **Shape** from the combobox. Refer https://www.compuphase.com/electronics/LibraryFileFormats.pdf for more information.

12. *__Optional:__* Select or de-select the **Invisible Pin** checkbox. Refer https://www.compuphase.com/electronics/LibraryFileFormats.pdf for more information.

13. Once the selected pin's attributes are finalized per the IC datasheet and one's satisfaction, one may click **Update Pin Attributes**. Repeat Steps 7-12 as many times as required.

14. *__Optional:__* Select or de-select the **Cross Hair** checkbox for better visual aid. 

15. One may **save** KiCAD IC Library Component to a drive. These may be later opened up in the KiCAD Library Component Editor Tool inside KiCAD EDA.

**Note: Currently $FPLIST (Foot print list) needs to be added manually post using this tool.**

![alt text](https://github.com/enthusiasticgeek/UKLCIG/blob/master/uklcig_screenshot0.png "UKLCIG")
