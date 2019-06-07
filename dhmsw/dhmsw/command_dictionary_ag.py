###############################################################################
#    command_dictionary_ag.py
#
#    IMPORTANT NOTE:  This file is auto-generated by the script: build_command_dictionary.py
#
#    Generated on:                 2019-02-04 10:51:10
#    Command dictionary filename:  command_dictionary.xml
#    Command dictionary version:   0.1
###############################################################################

CmdDict = {}
CmdDict["reconst"] = {}
CmdDict["reconst"]["propagation_distance"] = {}
CmdDict["reconst"]["propagation_distance"]["type"] = float
CmdDict["reconst"]["propagation_distance"]["islist"] = True
CmdDict["reconst"]["propagation_distance"]["maxcount"] = 3
CmdDict["reconst"]["propagation_distance"]["minvalue"] = -100
CmdDict["reconst"]["propagation_distance"]["maxvalue"] = 100
CmdDict["reconst"]["propagation_distance"]["enumlist"] = []
CmdDict["reconst"]["propagation_distance"]["units"] = "meters"
CmdDict["reconst"]["propagation_distance"]["description"] = ""
CmdDict["reconst"]["compute_spectral_peak"] = {}
CmdDict["reconst"]["compute_spectral_peak"]["type"] = bool
CmdDict["reconst"]["compute_spectral_peak"]["islist"] = False
CmdDict["reconst"]["compute_spectral_peak"]["maxcount"] = 1
CmdDict["reconst"]["compute_spectral_peak"]["minvalue"] = True
CmdDict["reconst"]["compute_spectral_peak"]["maxvalue"] = True
CmdDict["reconst"]["compute_spectral_peak"]["enumlist"] = []
CmdDict["reconst"]["compute_spectral_peak"]["units"] = ""
CmdDict["reconst"]["compute_spectral_peak"]["description"] = ""
CmdDict["reconst"]["compute_digital_phase_mask"] = {}
CmdDict["reconst"]["compute_digital_phase_mask"]["type"] = bool
CmdDict["reconst"]["compute_digital_phase_mask"]["islist"] = False
CmdDict["reconst"]["compute_digital_phase_mask"]["maxcount"] = 1
CmdDict["reconst"]["compute_digital_phase_mask"]["minvalue"] = True
CmdDict["reconst"]["compute_digital_phase_mask"]["maxvalue"] = True
CmdDict["reconst"]["compute_digital_phase_mask"]["enumlist"] = []
CmdDict["reconst"]["compute_digital_phase_mask"]["units"] = ""
CmdDict["reconst"]["compute_digital_phase_mask"]["description"] = ""
CmdDict["reconst"]["processing_mode"] = {}
CmdDict["reconst"]["processing_mode"]["type"] = str
CmdDict["reconst"]["processing_mode"]["islist"] = False
CmdDict["reconst"]["processing_mode"]["maxcount"] = 1
CmdDict["reconst"]["processing_mode"]["minvalue"] = None
CmdDict["reconst"]["processing_mode"]["maxvalue"] = None
CmdDict["reconst"]["processing_mode"]["enumlist"] = ["OFF","AMP","INTENSITY","PHASE","AMP_AND_PHASE","INT_AND_PHASE","ALL",]
CmdDict["reconst"]["processing_mode"]["units"] = ""
CmdDict["reconst"]["processing_mode"]["description"] = ""
CmdDict["reconst"]["chromatic_shift"] = {}
CmdDict["reconst"]["chromatic_shift"]["type"] = float
CmdDict["reconst"]["chromatic_shift"]["islist"] = True
CmdDict["reconst"]["chromatic_shift"]["maxcount"] = 3
CmdDict["reconst"]["chromatic_shift"]["minvalue"] = 1e-07
CmdDict["reconst"]["chromatic_shift"]["maxvalue"] = -1e-07
CmdDict["reconst"]["chromatic_shift"]["enumlist"] = []
CmdDict["reconst"]["chromatic_shift"]["units"] = "meters"
CmdDict["reconst"]["chromatic_shift"]["description"] = ""
CmdDict["reconst"]["ref_holo_path"] = {}
CmdDict["reconst"]["ref_holo_path"]["type"] = str
CmdDict["reconst"]["ref_holo_path"]["islist"] = False
CmdDict["reconst"]["ref_holo_path"]["maxcount"] = 1
CmdDict["reconst"]["ref_holo_path"]["minvalue"] = None
CmdDict["reconst"]["ref_holo_path"]["maxvalue"] = None
CmdDict["reconst"]["ref_holo_path"]["enumlist"] = []
CmdDict["reconst"]["ref_holo_path"]["units"] = ""
CmdDict["reconst"]["ref_holo_path"]["description"] = ""
CmdDict["reconst"]["ref_holo_enable"] = {}
CmdDict["reconst"]["ref_holo_enable"]["type"] = bool
CmdDict["reconst"]["ref_holo_enable"]["islist"] = False
CmdDict["reconst"]["ref_holo_enable"]["maxcount"] = 1
CmdDict["reconst"]["ref_holo_enable"]["minvalue"] = True
CmdDict["reconst"]["ref_holo_enable"]["maxvalue"] = True
CmdDict["reconst"]["ref_holo_enable"]["enumlist"] = []
CmdDict["reconst"]["ref_holo_enable"]["units"] = ""
CmdDict["reconst"]["ref_holo_enable"]["description"] = ""
CmdDict["reconst"]["ref_holo_save"] = {}
CmdDict["reconst"]["ref_holo_save"]["type"] = bool
CmdDict["reconst"]["ref_holo_save"]["islist"] = False
CmdDict["reconst"]["ref_holo_save"]["maxcount"] = 1
CmdDict["reconst"]["ref_holo_save"]["minvalue"] = True
CmdDict["reconst"]["ref_holo_save"]["maxvalue"] = True
CmdDict["reconst"]["ref_holo_save"]["enumlist"] = []
CmdDict["reconst"]["ref_holo_save"]["units"] = ""
CmdDict["reconst"]["ref_holo_save"]["description"] = ""
CmdDict["reconst"]["ref_holo_averaging_sec"] = {}
CmdDict["reconst"]["ref_holo_averaging_sec"]["type"] = float
CmdDict["reconst"]["ref_holo_averaging_sec"]["islist"] = False
CmdDict["reconst"]["ref_holo_averaging_sec"]["maxcount"] = 1
CmdDict["reconst"]["ref_holo_averaging_sec"]["minvalue"] = 0
CmdDict["reconst"]["ref_holo_averaging_sec"]["maxvalue"] = 60
CmdDict["reconst"]["ref_holo_averaging_sec"]["enumlist"] = []
CmdDict["reconst"]["ref_holo_averaging_sec"]["units"] = "Seconds"
CmdDict["reconst"]["ref_holo_averaging_sec"]["description"] = ""
CmdDict["reconst"]["ref_holo_averaging_enable"] = {}
CmdDict["reconst"]["ref_holo_averaging_enable"]["type"] = bool
CmdDict["reconst"]["ref_holo_averaging_enable"]["islist"] = False
CmdDict["reconst"]["ref_holo_averaging_enable"]["maxcount"] = 1
CmdDict["reconst"]["ref_holo_averaging_enable"]["minvalue"] = True
CmdDict["reconst"]["ref_holo_averaging_enable"]["maxvalue"] = True
CmdDict["reconst"]["ref_holo_averaging_enable"]["enumlist"] = []
CmdDict["reconst"]["ref_holo_averaging_enable"]["units"] = ""
CmdDict["reconst"]["ref_holo_averaging_enable"]["description"] = ""
CmdDict["reconst"]["phase_unwrapping_enable"] = {}
CmdDict["reconst"]["phase_unwrapping_enable"]["type"] = bool
CmdDict["reconst"]["phase_unwrapping_enable"]["islist"] = False
CmdDict["reconst"]["phase_unwrapping_enable"]["maxcount"] = 1
CmdDict["reconst"]["phase_unwrapping_enable"]["minvalue"] = True
CmdDict["reconst"]["phase_unwrapping_enable"]["maxvalue"] = True
CmdDict["reconst"]["phase_unwrapping_enable"]["enumlist"] = []
CmdDict["reconst"]["phase_unwrapping_enable"]["units"] = ""
CmdDict["reconst"]["phase_unwrapping_enable"]["description"] = ""
CmdDict["reconst"]["phase_unwrapping_algorithm"] = {}
CmdDict["reconst"]["phase_unwrapping_algorithm"]["type"] = str
CmdDict["reconst"]["phase_unwrapping_algorithm"]["islist"] = False
CmdDict["reconst"]["phase_unwrapping_algorithm"]["maxcount"] = 1
CmdDict["reconst"]["phase_unwrapping_algorithm"]["minvalue"] = None
CmdDict["reconst"]["phase_unwrapping_algorithm"]["maxvalue"] = None
CmdDict["reconst"]["phase_unwrapping_algorithm"]["enumlist"] = ["NONE",]
CmdDict["reconst"]["phase_unwrapping_algorithm"]["units"] = ""
CmdDict["reconst"]["phase_unwrapping_algorithm"]["description"] = ""
CmdDict["reconst"]["fitting_mode"] = {}
CmdDict["reconst"]["fitting_mode"]["type"] = str
CmdDict["reconst"]["fitting_mode"]["islist"] = False
CmdDict["reconst"]["fitting_mode"]["maxcount"] = 1
CmdDict["reconst"]["fitting_mode"]["minvalue"] = None
CmdDict["reconst"]["fitting_mode"]["maxvalue"] = None
CmdDict["reconst"]["fitting_mode"]["enumlist"] = ["NONE","1D_SEGMENT","2D_SEGMENT",]
CmdDict["reconst"]["fitting_mode"]["units"] = "NONE"
CmdDict["reconst"]["fitting_mode"]["description"] = ""
CmdDict["reconst"]["fitting_method"] = {}
CmdDict["reconst"]["fitting_method"]["type"] = str
CmdDict["reconst"]["fitting_method"]["islist"] = False
CmdDict["reconst"]["fitting_method"]["maxcount"] = 1
CmdDict["reconst"]["fitting_method"]["minvalue"] = None
CmdDict["reconst"]["fitting_method"]["maxvalue"] = None
CmdDict["reconst"]["fitting_method"]["enumlist"] = ["NONE","POLYNOMIAL",]
CmdDict["reconst"]["fitting_method"]["units"] = "NONE"
CmdDict["reconst"]["fitting_method"]["description"] = ""
CmdDict["reconst"]["fitting_order"] = {}
CmdDict["reconst"]["fitting_order"]["type"] = float
CmdDict["reconst"]["fitting_order"]["islist"] = False
CmdDict["reconst"]["fitting_order"]["maxcount"] = 1
CmdDict["reconst"]["fitting_order"]["minvalue"] = 0
CmdDict["reconst"]["fitting_order"]["maxvalue"] = 5
CmdDict["reconst"]["fitting_order"]["enumlist"] = []
CmdDict["reconst"]["fitting_order"]["units"] = ""
CmdDict["reconst"]["fitting_order"]["description"] = ""
CmdDict["reconst"]["fitting_apply"] = {}
CmdDict["reconst"]["fitting_apply"]["type"] = bool
CmdDict["reconst"]["fitting_apply"]["islist"] = False
CmdDict["reconst"]["fitting_apply"]["maxcount"] = 1
CmdDict["reconst"]["fitting_apply"]["minvalue"] = True
CmdDict["reconst"]["fitting_apply"]["maxvalue"] = True
CmdDict["reconst"]["fitting_apply"]["enumlist"] = []
CmdDict["reconst"]["fitting_apply"]["units"] = ""
CmdDict["reconst"]["fitting_apply"]["description"] = ""
CmdDict["reconst"]["reset_phase_mask"] = {}
CmdDict["reconst"]["reset_phase_mask"]["type"] = bool
CmdDict["reconst"]["reset_phase_mask"]["islist"] = False
CmdDict["reconst"]["reset_phase_mask"]["maxcount"] = 1
CmdDict["reconst"]["reset_phase_mask"]["minvalue"] = True
CmdDict["reconst"]["reset_phase_mask"]["maxvalue"] = True
CmdDict["reconst"]["reset_phase_mask"]["enumlist"] = []
CmdDict["reconst"]["reset_phase_mask"]["units"] = ""
CmdDict["reconst"]["reset_phase_mask"]["description"] = ""
CmdDict["reconst"]["roi_offset_x"] = {}
CmdDict["reconst"]["roi_offset_x"]["type"] = int
CmdDict["reconst"]["roi_offset_x"]["islist"] = False
CmdDict["reconst"]["roi_offset_x"]["maxcount"] = 1
CmdDict["reconst"]["roi_offset_x"]["minvalue"] = 0
CmdDict["reconst"]["roi_offset_x"]["maxvalue"] = 2048
CmdDict["reconst"]["roi_offset_x"]["enumlist"] = []
CmdDict["reconst"]["roi_offset_x"]["units"] = ""
CmdDict["reconst"]["roi_offset_x"]["description"] = ""
CmdDict["reconst"]["roi_offset_y"] = {}
CmdDict["reconst"]["roi_offset_y"]["type"] = int
CmdDict["reconst"]["roi_offset_y"]["islist"] = False
CmdDict["reconst"]["roi_offset_y"]["maxcount"] = 1
CmdDict["reconst"]["roi_offset_y"]["minvalue"] = 0
CmdDict["reconst"]["roi_offset_y"]["maxvalue"] = 2048
CmdDict["reconst"]["roi_offset_y"]["enumlist"] = []
CmdDict["reconst"]["roi_offset_y"]["units"] = ""
CmdDict["reconst"]["roi_offset_y"]["description"] = ""
CmdDict["reconst"]["roi_size_x"] = {}
CmdDict["reconst"]["roi_size_x"]["type"] = int
CmdDict["reconst"]["roi_size_x"]["islist"] = False
CmdDict["reconst"]["roi_size_x"]["maxcount"] = 1
CmdDict["reconst"]["roi_size_x"]["minvalue"] = 0
CmdDict["reconst"]["roi_size_x"]["maxvalue"] = 2048
CmdDict["reconst"]["roi_size_x"]["enumlist"] = []
CmdDict["reconst"]["roi_size_x"]["units"] = ""
CmdDict["reconst"]["roi_size_x"]["description"] = ""
CmdDict["reconst"]["roi_size_y"] = {}
CmdDict["reconst"]["roi_size_y"]["type"] = int
CmdDict["reconst"]["roi_size_y"]["islist"] = False
CmdDict["reconst"]["roi_size_y"]["maxcount"] = 1
CmdDict["reconst"]["roi_size_y"]["minvalue"] = 0
CmdDict["reconst"]["roi_size_y"]["maxvalue"] = 2048
CmdDict["reconst"]["roi_size_y"]["enumlist"] = []
CmdDict["reconst"]["roi_size_y"]["units"] = ""
CmdDict["reconst"]["roi_size_y"]["description"] = ""
CmdDict["reconst"]["store_files"] = {}
CmdDict["reconst"]["store_files"]["type"] = bool
CmdDict["reconst"]["store_files"]["islist"] = False
CmdDict["reconst"]["store_files"]["maxcount"] = 1
CmdDict["reconst"]["store_files"]["minvalue"] = True
CmdDict["reconst"]["store_files"]["maxvalue"] = True
CmdDict["reconst"]["store_files"]["enumlist"] = []
CmdDict["reconst"]["store_files"]["units"] = ""
CmdDict["reconst"]["store_files"]["description"] = ""
CmdDict["reconst"]["center_image"] = {}
CmdDict["reconst"]["center_image"]["type"] = bool
CmdDict["reconst"]["center_image"]["islist"] = False
CmdDict["reconst"]["center_image"]["maxcount"] = 1
CmdDict["reconst"]["center_image"]["minvalue"] = True
CmdDict["reconst"]["center_image"]["maxvalue"] = True
CmdDict["reconst"]["center_image"]["enumlist"] = []
CmdDict["reconst"]["center_image"]["units"] = ""
CmdDict["reconst"]["center_image"]["description"] = ""
CmdDict["reconst"]["center_image_and_tilt"] = {}
CmdDict["reconst"]["center_image_and_tilt"]["type"] = bool
CmdDict["reconst"]["center_image_and_tilt"]["islist"] = False
CmdDict["reconst"]["center_image_and_tilt"]["maxcount"] = 1
CmdDict["reconst"]["center_image_and_tilt"]["minvalue"] = True
CmdDict["reconst"]["center_image_and_tilt"]["maxvalue"] = True
CmdDict["reconst"]["center_image_and_tilt"]["enumlist"] = []
CmdDict["reconst"]["center_image_and_tilt"]["units"] = ""
CmdDict["reconst"]["center_image_and_tilt"]["description"] = ""
CmdDict["reconst"]["center_max_value"] = {}
CmdDict["reconst"]["center_max_value"]["type"] = bool
CmdDict["reconst"]["center_max_value"]["islist"] = False
CmdDict["reconst"]["center_max_value"]["maxcount"] = 1
CmdDict["reconst"]["center_max_value"]["minvalue"] = True
CmdDict["reconst"]["center_max_value"]["maxvalue"] = True
CmdDict["reconst"]["center_max_value"]["enumlist"] = []
CmdDict["reconst"]["center_max_value"]["units"] = ""
CmdDict["reconst"]["center_max_value"]["description"] = ""
CmdDict["reconst"]["center_wide_spectrum"] = {}
CmdDict["reconst"]["center_wide_spectrum"]["type"] = bool
CmdDict["reconst"]["center_wide_spectrum"]["islist"] = False
CmdDict["reconst"]["center_wide_spectrum"]["maxcount"] = 1
CmdDict["reconst"]["center_wide_spectrum"]["minvalue"] = True
CmdDict["reconst"]["center_wide_spectrum"]["maxvalue"] = True
CmdDict["reconst"]["center_wide_spectrum"]["enumlist"] = []
CmdDict["reconst"]["center_wide_spectrum"]["units"] = ""
CmdDict["reconst"]["center_wide_spectrum"]["description"] = ""
CmdDict["holo"] = {}
CmdDict["holo"]["wavelength"] = {}
CmdDict["holo"]["wavelength"]["type"] = float
CmdDict["holo"]["wavelength"]["islist"] = True
CmdDict["holo"]["wavelength"]["maxcount"] = 3
CmdDict["holo"]["wavelength"]["minvalue"] = 2e-07
CmdDict["holo"]["wavelength"]["maxvalue"] = 7e-07
CmdDict["holo"]["wavelength"]["enumlist"] = []
CmdDict["holo"]["wavelength"]["units"] = "meters"
CmdDict["holo"]["wavelength"]["description"] = ""
CmdDict["holo"]["dx"] = {}
CmdDict["holo"]["dx"]["type"] = float
CmdDict["holo"]["dx"]["islist"] = False
CmdDict["holo"]["dx"]["maxcount"] = 1
CmdDict["holo"]["dx"]["minvalue"] = 200
CmdDict["holo"]["dx"]["maxvalue"] = 700
CmdDict["holo"]["dx"]["enumlist"] = []
CmdDict["holo"]["dx"]["units"] = "meters"
CmdDict["holo"]["dx"]["description"] = ""
CmdDict["holo"]["dy"] = {}
CmdDict["holo"]["dy"]["type"] = float
CmdDict["holo"]["dy"]["islist"] = False
CmdDict["holo"]["dy"]["maxcount"] = 1
CmdDict["holo"]["dy"]["minvalue"] = 200
CmdDict["holo"]["dy"]["maxvalue"] = 700
CmdDict["holo"]["dy"]["enumlist"] = []
CmdDict["holo"]["dy"]["units"] = "meters"
CmdDict["holo"]["dy"]["description"] = ""
CmdDict["holo"]["crop_fraction"] = {}
CmdDict["holo"]["crop_fraction"]["type"] = int
CmdDict["holo"]["crop_fraction"]["islist"] = False
CmdDict["holo"]["crop_fraction"]["maxcount"] = 1
CmdDict["holo"]["crop_fraction"]["minvalue"] = 0
CmdDict["holo"]["crop_fraction"]["maxvalue"] = 0
CmdDict["holo"]["crop_fraction"]["enumlist"] = []
CmdDict["holo"]["crop_fraction"]["units"] = ""
CmdDict["holo"]["crop_fraction"]["description"] = ""
CmdDict["holo"]["rebin_factor"] = {}
CmdDict["holo"]["rebin_factor"]["type"] = int
CmdDict["holo"]["rebin_factor"]["islist"] = False
CmdDict["holo"]["rebin_factor"]["maxcount"] = 1
CmdDict["holo"]["rebin_factor"]["minvalue"] = 0
CmdDict["holo"]["rebin_factor"]["maxvalue"] = 0
CmdDict["holo"]["rebin_factor"]["enumlist"] = []
CmdDict["holo"]["rebin_factor"]["units"] = ""
CmdDict["holo"]["rebin_factor"]["description"] = ""
CmdDict["holo"]["bgd_sub"] = {}
CmdDict["holo"]["bgd_sub"]["type"] = bool
CmdDict["holo"]["bgd_sub"]["islist"] = False
CmdDict["holo"]["bgd_sub"]["maxcount"] = 1
CmdDict["holo"]["bgd_sub"]["minvalue"] = True
CmdDict["holo"]["bgd_sub"]["maxvalue"] = True
CmdDict["holo"]["bgd_sub"]["enumlist"] = []
CmdDict["holo"]["bgd_sub"]["units"] = ""
CmdDict["holo"]["bgd_sub"]["description"] = ""
CmdDict["holo"]["bgd_file"] = {}
CmdDict["holo"]["bgd_file"]["type"] = str
CmdDict["holo"]["bgd_file"]["islist"] = False
CmdDict["holo"]["bgd_file"]["maxcount"] = 1
CmdDict["holo"]["bgd_file"]["minvalue"] = None
CmdDict["holo"]["bgd_file"]["maxvalue"] = None
CmdDict["holo"]["bgd_file"]["enumlist"] = []
CmdDict["holo"]["bgd_file"]["units"] = ""
CmdDict["holo"]["bgd_file"]["description"] = ""
CmdDict["framesource"] = {}
CmdDict["framesource"]["mode"] = {}
CmdDict["framesource"]["mode"]["type"] = str
CmdDict["framesource"]["mode"]["islist"] = False
CmdDict["framesource"]["mode"]["maxcount"] = 1
CmdDict["framesource"]["mode"]["minvalue"] = None
CmdDict["framesource"]["mode"]["maxvalue"] = None
CmdDict["framesource"]["mode"]["enumlist"] = ["FILE","CAMERA","SEQUENCE",]
CmdDict["framesource"]["mode"]["units"] = ""
CmdDict["framesource"]["mode"]["description"] = ""
CmdDict["framesource"]["filepath"] = {}
CmdDict["framesource"]["filepath"]["type"] = str
CmdDict["framesource"]["filepath"]["islist"] = False
CmdDict["framesource"]["filepath"]["maxcount"] = 1
CmdDict["framesource"]["filepath"]["minvalue"] = None
CmdDict["framesource"]["filepath"]["maxvalue"] = None
CmdDict["framesource"]["filepath"]["enumlist"] = []
CmdDict["framesource"]["filepath"]["units"] = ""
CmdDict["framesource"]["filepath"]["description"] = ""
CmdDict["framesource"]["exec"] = {}
CmdDict["framesource"]["exec"]["type"] = str
CmdDict["framesource"]["exec"]["islist"] = False
CmdDict["framesource"]["exec"]["maxcount"] = 1
CmdDict["framesource"]["exec"]["minvalue"] = None
CmdDict["framesource"]["exec"]["maxvalue"] = None
CmdDict["framesource"]["exec"]["enumlist"] = ["IDLE","RUN",]
CmdDict["framesource"]["exec"]["units"] = ""
CmdDict["framesource"]["exec"]["description"] = ""
CmdDict["session"] = {}
CmdDict["session"]["name"] = {}
CmdDict["session"]["name"]["type"] = str
CmdDict["session"]["name"]["islist"] = False
CmdDict["session"]["name"]["maxcount"] = 1
CmdDict["session"]["name"]["minvalue"] = None
CmdDict["session"]["name"]["maxvalue"] = None
CmdDict["session"]["name"]["enumlist"] = []
CmdDict["session"]["name"]["units"] = ""
CmdDict["session"]["name"]["description"] = ""
CmdDict["session"]["description"] = {}
CmdDict["session"]["description"]["type"] = str
CmdDict["session"]["description"]["islist"] = False
CmdDict["session"]["description"]["maxcount"] = 1
CmdDict["session"]["description"]["minvalue"] = None
CmdDict["session"]["description"]["maxvalue"] = None
CmdDict["session"]["description"]["enumlist"] = []
CmdDict["session"]["description"]["units"] = ""
CmdDict["session"]["description"]["description"] = ""
CmdDict["session"]["wavelength"] = {}
CmdDict["session"]["wavelength"]["type"] = float
CmdDict["session"]["wavelength"]["islist"] = True
CmdDict["session"]["wavelength"]["maxcount"] = 3
CmdDict["session"]["wavelength"]["minvalue"] = 2e-07
CmdDict["session"]["wavelength"]["maxvalue"] = 7e-07
CmdDict["session"]["wavelength"]["enumlist"] = []
CmdDict["session"]["wavelength"]["units"] = "meters"
CmdDict["session"]["wavelength"]["description"] = ""
CmdDict["session"]["dx"] = {}
CmdDict["session"]["dx"]["type"] = float
CmdDict["session"]["dx"]["islist"] = False
CmdDict["session"]["dx"]["maxcount"] = 1
CmdDict["session"]["dx"]["minvalue"] = 200
CmdDict["session"]["dx"]["maxvalue"] = 700
CmdDict["session"]["dx"]["enumlist"] = []
CmdDict["session"]["dx"]["units"] = "meters"
CmdDict["session"]["dx"]["description"] = ""
CmdDict["session"]["dy"] = {}
CmdDict["session"]["dy"]["type"] = float
CmdDict["session"]["dy"]["islist"] = False
CmdDict["session"]["dy"]["maxcount"] = 1
CmdDict["session"]["dy"]["minvalue"] = 200
CmdDict["session"]["dy"]["maxvalue"] = 700
CmdDict["session"]["dy"]["enumlist"] = []
CmdDict["session"]["dy"]["units"] = "meters"
CmdDict["session"]["dy"]["description"] = ""
CmdDict["session"]["crop_fraction"] = {}
CmdDict["session"]["crop_fraction"]["type"] = int
CmdDict["session"]["crop_fraction"]["islist"] = False
CmdDict["session"]["crop_fraction"]["maxcount"] = 1
CmdDict["session"]["crop_fraction"]["minvalue"] = 0
CmdDict["session"]["crop_fraction"]["maxvalue"] = 0
CmdDict["session"]["crop_fraction"]["enumlist"] = []
CmdDict["session"]["crop_fraction"]["units"] = ""
CmdDict["session"]["crop_fraction"]["description"] = ""
CmdDict["session"]["rebin_factor"] = {}
CmdDict["session"]["rebin_factor"]["type"] = int
CmdDict["session"]["rebin_factor"]["islist"] = False
CmdDict["session"]["rebin_factor"]["maxcount"] = 1
CmdDict["session"]["rebin_factor"]["minvalue"] = 0
CmdDict["session"]["rebin_factor"]["maxvalue"] = 0
CmdDict["session"]["rebin_factor"]["enumlist"] = []
CmdDict["session"]["rebin_factor"]["units"] = ""
CmdDict["session"]["rebin_factor"]["description"] = ""
CmdDict["session"]["focal_length"] = {}
CmdDict["session"]["focal_length"]["type"] = float
CmdDict["session"]["focal_length"]["islist"] = False
CmdDict["session"]["focal_length"]["maxcount"] = 1
CmdDict["session"]["focal_length"]["minvalue"] = 0.001
CmdDict["session"]["focal_length"]["maxvalue"] = 0.02
CmdDict["session"]["focal_length"]["enumlist"] = []
CmdDict["session"]["focal_length"]["units"] = "meters"
CmdDict["session"]["focal_length"]["description"] = ""
CmdDict["session"]["numerical_aperture"] = {}
CmdDict["session"]["numerical_aperture"]["type"] = float
CmdDict["session"]["numerical_aperture"]["islist"] = False
CmdDict["session"]["numerical_aperture"]["maxcount"] = 1
CmdDict["session"]["numerical_aperture"]["minvalue"] = 0.1
CmdDict["session"]["numerical_aperture"]["maxvalue"] = 1
CmdDict["session"]["numerical_aperture"]["enumlist"] = []
CmdDict["session"]["numerical_aperture"]["units"] = ""
CmdDict["session"]["numerical_aperture"]["description"] = ""
CmdDict["session"]["system_magnification"] = {}
CmdDict["session"]["system_magnification"]["type"] = float
CmdDict["session"]["system_magnification"]["islist"] = False
CmdDict["session"]["system_magnification"]["maxcount"] = 1
CmdDict["session"]["system_magnification"]["minvalue"] = 1
CmdDict["session"]["system_magnification"]["maxvalue"] = 200
CmdDict["session"]["system_magnification"]["enumlist"] = []
CmdDict["session"]["system_magnification"]["units"] = ""
CmdDict["session"]["system_magnification"]["description"] = ""
CmdDict["guiserver"] = {}
CmdDict["guiserver"]["enable_rawframes"] = {}
CmdDict["guiserver"]["enable_rawframes"]["type"] = bool
CmdDict["guiserver"]["enable_rawframes"]["islist"] = False
CmdDict["guiserver"]["enable_rawframes"]["maxcount"] = 1
CmdDict["guiserver"]["enable_rawframes"]["minvalue"] = True
CmdDict["guiserver"]["enable_rawframes"]["maxvalue"] = True
CmdDict["guiserver"]["enable_rawframes"]["enumlist"] = []
CmdDict["guiserver"]["enable_rawframes"]["units"] = ""
CmdDict["guiserver"]["enable_rawframes"]["description"] = ""
CmdDict["guiserver"]["enable_fourier"] = {}
CmdDict["guiserver"]["enable_fourier"]["type"] = bool
CmdDict["guiserver"]["enable_fourier"]["islist"] = False
CmdDict["guiserver"]["enable_fourier"]["maxcount"] = 1
CmdDict["guiserver"]["enable_fourier"]["minvalue"] = True
CmdDict["guiserver"]["enable_fourier"]["maxvalue"] = True
CmdDict["guiserver"]["enable_fourier"]["enumlist"] = []
CmdDict["guiserver"]["enable_fourier"]["units"] = ""
CmdDict["guiserver"]["enable_fourier"]["description"] = ""
CmdDict["guiserver"]["enable_amplitude"] = {}
CmdDict["guiserver"]["enable_amplitude"]["type"] = bool
CmdDict["guiserver"]["enable_amplitude"]["islist"] = False
CmdDict["guiserver"]["enable_amplitude"]["maxcount"] = 1
CmdDict["guiserver"]["enable_amplitude"]["minvalue"] = True
CmdDict["guiserver"]["enable_amplitude"]["maxvalue"] = True
CmdDict["guiserver"]["enable_amplitude"]["enumlist"] = []
CmdDict["guiserver"]["enable_amplitude"]["units"] = ""
CmdDict["guiserver"]["enable_amplitude"]["description"] = ""
CmdDict["guiserver"]["enable_intensity"] = {}
CmdDict["guiserver"]["enable_intensity"]["type"] = bool
CmdDict["guiserver"]["enable_intensity"]["islist"] = False
CmdDict["guiserver"]["enable_intensity"]["maxcount"] = 1
CmdDict["guiserver"]["enable_intensity"]["minvalue"] = True
CmdDict["guiserver"]["enable_intensity"]["maxvalue"] = True
CmdDict["guiserver"]["enable_intensity"]["enumlist"] = []
CmdDict["guiserver"]["enable_intensity"]["units"] = ""
CmdDict["guiserver"]["enable_intensity"]["description"] = ""
CmdDict["guiserver"]["enable_phase"] = {}
CmdDict["guiserver"]["enable_phase"]["type"] = bool
CmdDict["guiserver"]["enable_phase"]["islist"] = False
CmdDict["guiserver"]["enable_phase"]["maxcount"] = 1
CmdDict["guiserver"]["enable_phase"]["minvalue"] = True
CmdDict["guiserver"]["enable_phase"]["maxvalue"] = True
CmdDict["guiserver"]["enable_phase"]["enumlist"] = []
CmdDict["guiserver"]["enable_phase"]["units"] = ""
CmdDict["guiserver"]["enable_phase"]["description"] = ""
CmdDict["datalogger"] = {}
CmdDict["datalogger"]["enabled"] = {}
CmdDict["datalogger"]["enabled"]["type"] = bool
CmdDict["datalogger"]["enabled"]["islist"] = False
CmdDict["datalogger"]["enabled"]["maxcount"] = 1
CmdDict["datalogger"]["enabled"]["minvalue"] = True
CmdDict["datalogger"]["enabled"]["maxvalue"] = True
CmdDict["datalogger"]["enabled"]["enumlist"] = []
CmdDict["datalogger"]["enabled"]["units"] = ""
CmdDict["datalogger"]["enabled"]["description"] = ""
CmdDict["datalogger"]["rootpath"] = {}
CmdDict["datalogger"]["rootpath"]["type"] = str
CmdDict["datalogger"]["rootpath"]["islist"] = False
CmdDict["datalogger"]["rootpath"]["maxcount"] = 1
CmdDict["datalogger"]["rootpath"]["minvalue"] = None
CmdDict["datalogger"]["rootpath"]["maxvalue"] = None
CmdDict["datalogger"]["rootpath"]["enumlist"] = []
CmdDict["datalogger"]["rootpath"]["units"] = ""
CmdDict["datalogger"]["rootpath"]["description"] = ""
CmdDict["fouriermask"] = {}
CmdDict["fouriermask"]["mask_circle_1"] = {}
CmdDict["fouriermask"]["mask_circle_1"]["type"] = int
CmdDict["fouriermask"]["mask_circle_1"]["islist"] = True
CmdDict["fouriermask"]["mask_circle_1"]["maxcount"] = 3
CmdDict["fouriermask"]["mask_circle_1"]["minvalue"] = 0
CmdDict["fouriermask"]["mask_circle_1"]["maxvalue"] = 2048
CmdDict["fouriermask"]["mask_circle_1"]["enumlist"] = []
CmdDict["fouriermask"]["mask_circle_1"]["units"] = ""
CmdDict["fouriermask"]["mask_circle_1"]["description"] = "Pixels X, Y and radius of circular mask"
CmdDict["fouriermask"]["mask_circle_2"] = {}
CmdDict["fouriermask"]["mask_circle_2"]["type"] = int
CmdDict["fouriermask"]["mask_circle_2"]["islist"] = True
CmdDict["fouriermask"]["mask_circle_2"]["maxcount"] = 3
CmdDict["fouriermask"]["mask_circle_2"]["minvalue"] = 0
CmdDict["fouriermask"]["mask_circle_2"]["maxvalue"] = 2048
CmdDict["fouriermask"]["mask_circle_2"]["enumlist"] = []
CmdDict["fouriermask"]["mask_circle_2"]["units"] = ""
CmdDict["fouriermask"]["mask_circle_2"]["description"] = "Pixels X, Y and radius of circular mask"
CmdDict["fouriermask"]["mask_circle_3"] = {}
CmdDict["fouriermask"]["mask_circle_3"]["type"] = int
CmdDict["fouriermask"]["mask_circle_3"]["islist"] = True
CmdDict["fouriermask"]["mask_circle_3"]["maxcount"] = 3
CmdDict["fouriermask"]["mask_circle_3"]["minvalue"] = 0
CmdDict["fouriermask"]["mask_circle_3"]["maxvalue"] = 2048
CmdDict["fouriermask"]["mask_circle_3"]["enumlist"] = []
CmdDict["fouriermask"]["mask_circle_3"]["units"] = ""
CmdDict["fouriermask"]["mask_circle_3"]["description"] = "Pixels X, Y and radius of circular mask"
CmdDict["shutdown"] = {}
CmdDict["no_op"] = {}
