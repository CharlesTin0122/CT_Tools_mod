import os
from animCurveFilter import CurveFilterFunctions as Cf
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtUiTools

user_path = os.getenv('HOME')
uifile_path = os.path.join(os.path.dirname(__file__), 'Filter_UI2.ui')


def loadui(uifile_path):
    uifile = QtCore.QFile(uifile_path)
    print(uifile)
    uifile.open(QtCore.QFile.ReadOnly)
    uiWindow = QtUiTools.QUiLoader().load(uifile)
    uifile.close()
    print('load ui')
    return uiWindow


class MainWindow:

    def __init__(self, parent=None):
        self.ui = loadui(uifile_path)
        self.ui.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.slots()
        self.kill_job()
        self.create_job()

    def slots(self):
        self.ui.reset.clicked.connect(self.reset_slider)
        self.ui.reset_2.clicked.connect(self.reset_slider)
        self.ui.combo.currentIndexChanged.connect(self.update_slider_function)
        self.ui.combo.currentIndexChanged.connect(self.ui_switch)
        self.ui.slider.sliderMoved.connect(self.empty)
        self.ui.slider.sliderPressed.connect(self.show_buffer)
        self.ui.buffer.clicked.connect(self.buffer_swap)
        self.ui.buffer.clicked.connect(self.noshow_buffer)
        self.ui.buffer.clicked.connect(self.create_buffer)

    def update_slider_function(self):
        if self.ui.combo.currentText() == 'Twinner':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.drag_twinner)
        if self.ui.combo.currentText() == 'Dampen':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.drag_scale)
        if self.ui.combo.currentText() == 'Butterworth':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.drag_butterworth)
        if self.ui.combo.currentText() == 'Smooth':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.drag_smooth)
        if self.ui.combo.currentText() == 'Simplify':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.drag_simplify)
        if self.ui.combo.currentText() == '...':
            self.ui.slider.sliderMoved.disconnect()
            self.ui.slider.sliderMoved.connect(self.empty)

    def empty(self):
        pass

    def drag_scale(self):
        value = self.ui.slider.value()
        optionValue = cmds.optionVar(q='defaultToto2')
        if value > optionValue:
            Cf.scalekey(0.9)
        elif value < optionValue:
            Cf.scalekey(1.1)
        cmds.optionVar(fv=('defaultToto2', value))

    def drag_twinner(self):
        value = self.ui.slider.value()
        optionValue = cmds.optionVar(q='defaultToto2')
        Cf.twinner(value)

    def drag_smooth(self):
        value = self.ui.slider.value()
        optionValue = cmds.optionVar(q='defaultToto2')
        if value > optionValue:
            Cf.smooth()
        cmds.optionVar(fv=('defaultToto2', value))

    def drag_butterworth(self):
        value = self.ui.slider.value()
        optionValue = cmds.optionVar(q='defaultToto2')
        if value > optionValue:
            Cf.butterworth(0.9)
        elif value < optionValue:
            Cf.butterworth(1.1)
        cmds.optionVar(fv=('defaultToto2', value))

    def drag_simplify(self):
        value = self.ui.slider.value()
        Cf.resampleDrag(value, 100)

    def buffer_swap(self):
        if not cmds.keyframe(sl=True, query=True, valueChange=True, absolute=True):
            pass
        mykeys = []
        if len(mykeys) > 0:
            cmds.bufferCurve(animation='keys', swap=True)
            self.reset_slider()

    def reset_slider(self):
        if self.ui.combo.currentText() == 'Smooth' or self.ui.combo.currentText() == 'Simplify':
            self.ui.slider.setValue(0)
        else:
            self.ui.slider.setValue(50)

    def create_buffer(self):
        cmds.bufferCurve(animation='keys', overwrite=True)
        print('buffer created')

    def show_buffer(self):
        cmds.animCurveEditor('graphEditor1GraphEd', edit=True, showBufferCurves='on')

    def noshow_buffer(self):
        cmds.animCurveEditor('graphEditor1GraphEd', edit=True, showBufferCurves='off')

    def ui_switch(self):
        if self.ui.combo.currentText() == 'Simplify':
            self.show_buffer()
            Cf.record()
        self.reset_slider()

    def selectChange_event(self):
        if not cmds.keyframe(sl=True, query=True, valueChange=True, absolute=True):
            pass
        mykeys = []
        if len(mykeys) > 0:
            if mykeys[0] != cmds.optionVar(q='jjs') or mykeys[-1] != cmds.optionVar(q='jje'):
                self.create_buffer()
                if self.ui.combo.currentText() == 'Simplify':
                    Cf.record()

            cmds.optionVar(fv=('jjs', mykeys[0]))
            cmds.optionVar(fv=('jje', mykeys[-1]))
        else:
            self.reset_slider()

    def create_job(self):
        self.jjob = cmds.scriptJob(e=[
            'SelectionChanged',
            self.selectChange_event])
        cmds.optionVar(fv=('job_id', self.jjob))

    def kill_job(self):
        job_id = cmds.optionVar(q='job_id')
        if job_id:
            cmds.scriptJob(kill=job_id, force=True)
            print('kkkkkkkkkkkkkkkkkkkilll scriptjob')

    def show(self):
        self.ui.show()


def main():
    mainWindow = MainWindow()
    mainWindow.show()
