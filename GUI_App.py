import os
import sys
from pathlib import Path

import numpy as np
import skimage.io as skio
import tifffile as tf
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QLineEdit, QGroupBox, QComboBox, QPushButton, QFileDialog,
                             QProgressDialog)

import util.inputoutput as io
from psf.psf import PSF
from util.deconvolution import Deconvolution


class Worker(QThread):
    """
    This class executes the main work and is called when the "Start the Deconvolution" Button is pressed
    """
    progress = pyqtSignal(int)
    message = pyqtSignal(str)

    def __init__(self, psf_parameters, decon_parameters, io_parameters, parent=None):
        super().__init__(parent)
        self.psf_data = psf_parameters
        self.decon_data = decon_parameters
        self.io_data = io_parameters

    def run(self):

        # ------------- load image -----------
        self.progress.emit(10)
        self.message.emit("Loading image") # send message to progress window
        img = skio.imread(self.io_data['read_path'])
        # correct shape if image not quadratic
        if img.ndim == 2:
            if img.shape[0] != img.shape[1]:
                minshape = np.min(img.shape)
                img = img[:minshape, :minshape]
            xdims = img.shape
        else:
            if img.shape[1] != img.shape[2]:
                minshape = np.min(img.shape)
                img = img[:, minshape, :minshape]
            xdims = (img.shape[1], img.shape[2])

        # ------------- create PSF ----------------
        self.psf_data['xysize'] = xdims[0]
        self.message.emit("Creating PSF")
        self.progress.emit(20)
        pf = PSF(xdims, **self.psf_data)
        # ------------- start deconvolution -------
        Dec = Deconvolution(pf.data, img, self.decon_data['lambda'],
                            self.decon_data['lambda_t'],
                            self.decon_data['epsilon'],
                            self.decon_data['max_iterations'], verbose=False)
        self.message.emit("Deconvolution in Progress")
        self.progress.emit(30)
        result = Dec.deconvolve()
        # ------------- save results -------
        io.set_baseline(img, result)
        os.makedirs(self.io_data['save_path'], exist_ok=True)
        self.message.emit("Saving Results")
        tf.imwrite(Path(self.io_data['save_path'], self.io_data['save_name']), result, photometric='minisblack')


class ParameterInputWindow(QMainWindow):
    """
    This class creates the main GUI input window where parameters are given
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Parameter Input")
        self.setGeometry(100, 100, 400, 300)

        main_widget = QFrame(self)
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        self.create_psf_section()
        self.create_decon_section()
        self.create_fileinput_section()

        layout.addWidget(self.psf_section)
        layout.addWidget(self.decon_section)
        layout.addWidget(self.fileinput_section)

        # Button to start the deconvolution
        self.show_progress_button = QPushButton("Start Deconvolution", main_widget)
        layout.addWidget(self.show_progress_button)
        self.show_progress_button.clicked.connect(self.show_progress_dialog)

# -------------------- PSF parameters ----------------------------


    def create_psf_section(self):
        self.psf_section = QGroupBox("PSF Parameters", self)
        psf_section_layout = QVBoxLayout(self.psf_section)

        self.type_label = QLabel("Microscope type", self.psf_section)
        psf_section_layout.addWidget(self.type_label)
        self.type_combo = QComboBox(self.psf_section)
        self.type_combo.addItems(["confocal", "widefield"])
        psf_section_layout.addWidget(self.type_combo)

        self.ex_label = QLabel("Excitation wavelength (nm)", self.psf_section)
        psf_section_layout.addWidget(self.ex_label)
        self.ex_entry = QLineEdit(self.psf_section)
        self.ex_entry.setText("488")
        psf_section_layout.addWidget(self.ex_entry)

        self.em_label = QLabel("Emission wavelength (nm)", self.psf_section)
        psf_section_layout.addWidget(self.em_label)
        self.em_entry = QLineEdit(self.psf_section)
        self.em_entry.setText("600")
        psf_section_layout.addWidget(self.em_entry)

        self.na_label = QLabel("Numerical aperture of the objective", self.psf_section)
        psf_section_layout.addWidget(self.na_label)
        self.na_entry = QLineEdit(self.psf_section)
        self.na_entry.setText("1.4")
        psf_section_layout.addWidget(self.na_entry)

        self.mo_label = QLabel("Objective total magnification", self.psf_section)
        psf_section_layout.addWidget(self.mo_label)
        self.mo_entry = QLineEdit(self.psf_section)
        self.mo_entry.setText("100")
        psf_section_layout.addWidget(self.mo_entry)

        self.rind_obj_label = QLabel("Refractive index of the objective immersion medium", self.psf_section)
        psf_section_layout.addWidget(self.rind_obj_label)
        self.rind_obj_entry = QLineEdit(self.psf_section)
        self.rind_obj_entry.setText("1.518")
        psf_section_layout.addWidget(self.rind_obj_entry)

        self.rind_sp_label = QLabel("Refractive index of the specimen medium", self.psf_section)
        psf_section_layout.addWidget(self.rind_sp_label)
        self.rind_sp_entry = QLineEdit(self.psf_section)
        self.rind_sp_entry.setText("1.518")
        psf_section_layout.addWidget(self.rind_sp_entry)

        self.ccd_label = QLabel("Pixel dimension of the CCD (in the plane of the camera)", self.psf_section)
        psf_section_layout.addWidget(self.ccd_label)
        self.ccd_entry = QLineEdit(self.psf_section)
        self.ccd_entry.setText("6450")
        psf_section_layout.addWidget(self.ccd_entry)

# -------------------- Deconvolution parameters ----------------------------

    def create_decon_section(self):
        self.decon_section = QGroupBox("Decon Parameters", self)
        decon_section_layout = QVBoxLayout(self.decon_section)

        self.lam_label = QLabel("𝝺 (weight for spatial regularization)", self.decon_section)
        decon_section_layout.addWidget(self.lam_label)
        self.lam_entry = QLineEdit(self.decon_section)
        self.lam_entry.setText("0.5")
        decon_section_layout.addWidget(self.lam_entry)

        self.lam_t_label = QLabel("𝝺_t (weight for temporal regularization)", self.decon_section)
        decon_section_layout.addWidget(self.lam_t_label)
        self.lam_t_entry = QLineEdit(self.decon_section)
        self.lam_t_entry.setText("0.5")
        decon_section_layout.addWidget(self.lam_t_entry)

# -------------------- input output parameters ----------------------------

    def create_fileinput_section(self):
        self.fileinput_section = QGroupBox("Input/ Output", self)
        fileinput_section_layout = QVBoxLayout(self.fileinput_section)

        self.input_label = QLabel("Select a file to process:", self.fileinput_section)
        fileinput_section_layout.addWidget(self.input_label)
        file_selector_layout = QHBoxLayout()
        self.file_path_label = QLabel("", self.fileinput_section)
        file_selector_layout.addWidget(self.file_path_label)

        select_file_btn = QPushButton("Browse", self.fileinput_section)
        select_file_btn.clicked.connect(self.select_file)
        file_selector_layout.addWidget(select_file_btn)

        fileinput_section_layout.addLayout(file_selector_layout)

        self.output_label = QLabel("Select a folder to save results in:", self.fileinput_section)
        fileinput_section_layout.addWidget(self.output_label)

        folder_selector_layout = QHBoxLayout()

        self.folder_path_label = QLabel("", self.fileinput_section)
        folder_selector_layout.addWidget(self.folder_path_label)

        select_folder_btn = QPushButton("Browse", self.fileinput_section)
        select_folder_btn.clicked.connect(self.select_folder)
        folder_selector_layout.addWidget(select_folder_btn)

        fileinput_section_layout.addLayout(folder_selector_layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName()
        self.file_path_label.setText(file_path)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory()
        self.folder_path_label.setText(folder_path)

    def set_parameter_dict(self):
        """
        save the GUI parameters into dictionaries
        """
        self.parameters = dict()
        self.psf_data = dict()
        self.psf_data['type'] = self.type_combo.currentText()
        self.psf_data['lambdaEx'] = float(self.ex_entry.text())
        self.psf_data['lambdaEm'] = float(self.em_entry.text())
        self.psf_data['numAper'] = float(self.na_entry.text())
        self.psf_data['magObj'] = float(self.mo_entry.text())
        self.psf_data['rindexObj'] = float(self.rind_obj_entry.text())
        self.psf_data['rindexSp'] = float(self.rind_sp_entry.text())
        self.psf_data['ccdSize'] = float(self.ccd_entry.text())
        self.psf_data['nor'] = 0
        self.psf_data['depth'] = 0
        self.psf_data['nslices'] = 1
        self.psf_data['dz'] = 0

        self.decon_data = dict()
        self.decon_data['lambda'] = float(self.lam_entry.text())
        self.decon_data['lambda_t'] = float(self.lam_t_entry.text())
        self.decon_data['epsilon'] = 0.001
        self.decon_data['max_iterations'] = 1
        self.decon_data['delta'] = 1

        self.io_data = dict()
        self.io_data['read_path'] = self.file_path_label.text()
        self.io_data['save_path'] = self.folder_path_label.text()
        fname = Path(self.io_data['read_path']).stem
        self.io_data['save_name'] = Path(fname, '_deconvolved.tif')


    def show_progress_dialog(self):
        """
        Show a small window with a progress bar and call the worker to execute the deconvolution
        """
        self.set_parameter_dict()
        self.worker = Worker(self.psf_data, self.decon_data, self.io_data)
        # set an indeterminate progress bar, for a "loading" bar, change the second "0" to "100"
        self.progress_dialog = QProgressDialog("Working...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowTitle("Deconvolution in Progress")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setMinimumDuration(10)

        # receive signals: progress status (if not indeterminate) and status message
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.message.connect(self.update_progress_label)
        self.worker.finished.connect(self.on_worker_finished)
        self.progress_dialog.canceled.connect(self.worker.terminate)

        self.worker.start()

    def on_worker_finished(self):
        self.close()

    def update_progress_label(self, message):
        self.progress_dialog.setLabelText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ParameterInputWindow()
    window.show()

    sys.exit(app.exec_())
