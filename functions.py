from constants import *

class DigitalGauge:
    def __init__(self, status, label, positionXY, font, label_font, label_XY, textColor = GREEN, labelTextcolor = TEXTCOLOUR):
        self.status = status
        self.label = label
        self.position = positionXY
        self.font = font
        self.fontObj = label_font
        self.label_XY = label_XY
        self.textColor = textColor
        self.labelTextcolor = labelTextcolor
        
    def draw(self):
        if self.label == 'Battery':
            self.text = self.font.render(str(float(self.status)), True, self.textColor)
        else:
            self.text = self.font.render(str(int(self.status)), True, self.textColor)
        
        self.text_rect = self.text.get_rect()
        self.text_rect.midright = self.position
        gauge_window.blit(self.text, self.text_rect)
        textSufaceObj = self.fontObj.render(self.label, True, TEXTCOLOUR, None)
        gauge_window.blit(textSufaceObj, self.label_XY)

class Indicator:
    def __init__(self):
        indicator_images = []
        resize_scaleXY = (48 , 35) 

    
