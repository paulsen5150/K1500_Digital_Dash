#functions31.pr
#Version 3.1 May 2026

from constants31 import *

class DigitalGauge:
    def __init__(self, status, label, position_XY, font, label_font, label_XY, textColor = GREEN, labelTextcolor = TEXTCOLOUR):
        #self.status = status
        self.label = label
        self.position_XY = position_XY
        self.font = font
        self.fontObj = label_font
        self.label_XY = label_XY
        self.textColor = textColor
        self.labelTextcolor = labelTextcolor
        
    def draw(self, status):
        self.status = status
        try:
            numeric_status = float(self.status)
        except (TypeError, ValueError):
            numeric_status = 0

        if self.label == 'Battery':
            self.text = self.font.render(str(numeric_status), True, self.textColor)
        else:
            self.text = self.font.render(str(int(numeric_status)), True, self.textColor)
        
        self.text_rect = self.text.get_rect()
        #self.text_rect.midright = self.position_XY
        self.text_rect.center = self.position_XY
        gauge_window.blit(self.text, self.text_rect)
        #gauge_window.blit(self.text, self.position_XY)
        textSufaceObj = self.fontObj.render(self.label, True, TEXTCOLOUR, None)
        gauge_window.blit(textSufaceObj, self.label_XY)

class Indicator:
    def __init__(self):
        indicator_images = []
        resize_scaleXY = (48 , 35) 

    
