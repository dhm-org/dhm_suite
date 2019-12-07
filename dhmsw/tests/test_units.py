import os
import pytest
import sys
#sys.path.insert(0, "../dhmsw/")
#import metadata_classes

class TestUnitMetadataTestClass(object):


    @classmethod
    def setup_class(cls):
        pass


    @classmethod
    def teardown_class(cls):
        pass


    def setup_method(cls, method):
        if method == cls.test_readMetaDictionaryGoodFile:
            CreateGoodConfigFile(goodFileName())
            pass
        elif method == cls.test_readMetaDictionaryBadFile:
            CreateBadConfigFile(badFileName())
            pass
        else:
            pass

    def teardown_method(cls, method):
        if method == cls.test_readMetaDictionaryGoodFile:
           os.remove(goodFileName())
        elif method == cls.test_readMetaDictionaryBadFile:
           os.remove(badFileName())
        else:
            pass

    def test_readMetaDictionaryGoodFile(cls, goodFileName):
        """Create a good file and ensure its read correctly"""
        #metadata_classes.Metadata_Dictionary(cls._configfile)
        pass
       

    def test_readMetaDictionaryBadFile(cls, badFileName):
        """Create a good file and ensure its read correctly"""
        assert True
    #    metadata_classes.Metadata_Dictionary(configfile)
    

@pytest.fixture
def goodFileName():
    return './goodconfig.ini'

@pytest.fixture
def badFileName():
    return './badconfig.ini'


def CreateGoodConfigFile(filename):

    contents = "[CONTROLLER]\n " +  \
        "cmd_hostname               = localhost\n" + \
        "cmd_port                   = 10000\n" + \
        "\n" + \
        "[GUISERVER]\n" + \
        "host                   = localhost\n" + \
        "maxclients             = 5\n" + \
        "fourier_port           = 9993\n" + \
        "reconst_amp_port       = 9994\n" + \
        "raw_frames_port        = 9995\n" + \
        "telemetry_port         = 9996\n" + \
        "reconst_intensity_port = 9997\n" + \
        "reconst_phase_port     = 9998\n" + \
        "\n" + \
        "[CAMERA_SERVER]\n" + \
        "host           = localhost\n" + \
        "frame_port     = 2000\n" + \
        "command_port   = 2001\n" + \
        "telemetry_port = 2002\n" + \
        "\n" + \
        "[DATALOGGER]\n" + \
        "enabled = yes\n" + \
        "\n" + \
        "[CAMERA]\n" + \
        "N = 2048\n" + \
        "\n" + \
        "[FRAMESOURCE]\n" + \
        "datadir               = test_frames/simulated_frames/*.bmp\n" + \
        "\n" + \
        "[HOLOGRAM]\n" + \
        "wavelength    = 405e-9\n" + \
        "dx            = 3.45e-6\n" + \
        "dy            = 3.45e-6\n" + \
        "crop_fraction = 0.\n" + \
        "rebin_factor  = 1\n" + \
        "bgd_sub       = false\n" + \
        "\n" + \
        "[RECONSTRUCTION]\n" + \
        "propagation_distance    = 0.01\n" + \
        "# Chromatic shift should have same number of values as wavelength\n" + \
        "chromatic_shift         = 0 \n" + \
        "compute_spectral_peak      = false \n" + \
        "compute_digital_phase_mask = false \n" + \
        "phase_mask_reset        = false\n" + \
        "fitting_apply           = false\n" + \
        "store_files             = false\n" + \
        "roi_pos_x               = 0\n" + \
        "roi_pos_y               = 0\n" + \
        "roi_size_x              = 2048\n" + \
        "roi_size_y              = 2048\n" + \
        "# Valid values [none|amplitude|phase|intensity|amp_and_phase|int_and_phase|all]\n" + \
        "processing_mode         = None\n" + \
        "\n" + \
        "[REFERENCE_HOLOGRAM]\n" + \
        "path              = path\n" + \
        "enabled           = false\n" + \
        "averaging_sec     = 0.0\n" + \
        "averaging_enabled = false\n" + \
        "\n" + \
        "[FITTING]\n" + \
        "# Valid values [none|1d_segment|2d_segment]\n" + \
        "mode = None\n" + \
        "# Valid values [none|polynomial]\n" + \
        "method = None\n" + \
        "order = 0\n" + \
        "applied = false\n" + \
        "\n" + \
        "[PHASE_UNWRAPPING]\n" + \
        "enabled = false\n" + \
        "# Valid values [none|algorithm_1|algorithm_2]\n" + \
        "algorithm = None\n" + \
        "\n" + \
        "[CENTER_IMAGE]\n" + \
        "center = false\n" + \
        "center_and_tilt = false\n" + \
        "max_value = false\n" + \
        "wide_spectrum = false\n" + \
        "\n" + \
        "[FOURIERMASK]\n" + \
        "center_x = 702, 1117, 1439\n" + \
        "center_y = 749, 6161, 893\n" + \
        "radius = 170, 170, 170\n" \

    with open(filename, 'w') as out_file:
        out_file.write(contents)

    return filename

def CreateBadConfigFile(filename):

    contents = "[CONTROLLER]\n " +  \
        "cmd_hostname               = localhost\n" + \
        "cmd_port                   = 10000\n" + \
        "\n" + \
        "[GUISERVER]\n" + \
        "host                   = localhost\n" + \
        "maxclients             = 5\n" + \
        "fourier_port           = 9993\n" + \
        "reconst_amp_port       = 9994\n" + \
        "raw_frames_port        = 9995\n" + \
        "telemetry_port         = 9996\n" + \
        "reconst_intensity_port = 9997\n" + \
        "reconst_phase_port     = 9998\n" + \
        "\n" + \
        "[CAMERA_SERVER]\n" + \
        "host           = localhost\n" + \
        "frame_port     = 2000\n" + \
        "command_port   = 2001\n" + \
        "telemetry_port = 2002\n" + \
        "\n" + \
        "[DATALOGGER]\n" + \
        "enabled = yes\n" + \
        "\n" + \
        "[CAMERA]\n" + \
        "N = 2048\n" + \
        "\n" + \
        "[FRAMESOURCE]\n" + \
        "datadir               = test_frames/simulated_frames/*.bmp\n" + \
        "\n" + \
        "[HOLOGRAM]\n" + \
        "wavelength    = 405e-9\n" + \
        "dx            = 3.45e-6\n" + \
        "dy            = 3.45e-6\n" + \
        "crop_fraction = 0.\n" + \
        "rebin_factor  = 1\n" + \
        "bgd_sub       = false\n" + \
        "\n" + \
        "[RECONSTRUCTION]\n" + \
        "propagation_distance    = 0.01\n" + \
        "# Chromatic shift should have same number of values as wavelength\n" + \
        "chromatic_shift         = 0 \n" + \
        "compute_spectral_peak      = false \n" + \
        "compute_digital_phase_mask = false \n" + \
        "phase_mask_reset        = false\n" + \
        "fitting_apply           = false\n" + \
        "store_files             = false\n" + \
        "roi_pos_x               = 0\n" + \
        "roi_pos_y               = 0\n" + \
        "roi_size_x              = 2048\n" + \
        "roi_size_y              = 2048\n" + \
        "# Valid values [none|amplitude|phase|intensity|amp_and_phase|int_and_phase|all]\n" + \
        "processing_mode         = None\n" + \
        "\n" + \
        "[REFERENCE_HOLOGRAM]\n" + \
        "path              = path\n" + \
        "enabled           = false\n" + \
        "averaging_sec     = 0.0\n" + \
        "averaging_enabled = false\n" + \
        "\n" + \
        "[FITTING]\n" + \
        "# Valid values [none|1d_segment|2d_segment]\n" + \
        "mode = None\n" + \
        "# Valid values [none|polynomial]\n" + \
        "method = None\n" + \
        "order = 0\n" + \
        "applied = false\n" + \
        "\n" + \
        "[PHASE_UNWRAPPING]\n" + \
        "enabled = false\n" + \
        "# Valid values [none|algorithm_1|algorithm_2]\n" + \
        "algorithm = None\n" + \
        "\n" + \
        "[CENTER_IMAGE]\n" + \
        "center = false\n" + \
        "center_and_tilt = false\n" + \
        "max_value = false\n" + \
        "wide_spectrum = false\n" + \
        "\n" + \
        "[FOURIERMASK]\n" + \
        "center_x = 702, 1117, 1439\n" + \
        "center_y = 749, 6161, 893\n" + \
        "radius = 170, 170, 170\n" \

    with open(filename, 'w') as out_file:
        out_file.write(contents)

