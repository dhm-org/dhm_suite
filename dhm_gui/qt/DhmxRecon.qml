import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.0


MouseArea {
    signal pack_cmd(string cmd)

    id: dhmx_recon
    visible: true
    width: 700
    height: 950
    transformOrigin: Item.TopLeft
    drag.target: dhmx_recon
    hoverEnabled: true

    property int prev_mouse_pos_x: 0



    Rectangle {
        id: drag_area
        anchors.fill: parent

        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4
    }

    /* Scaling handle */
    Button{
        id: button_resize
        x: 670
        y: 921
        width: 25
        height :25
        display: AbstractButton.IconOnly
        icon.source: "images/ui_handle.png"

        MouseArea{
            anchors.fill: parent
            property var cur_mouse_pos
            property var prev_mouse_pos_x: 0
            onPressed: {
                cur_mouse_pos = mouse.x
            }

            onPositionChanged: {
                cur_mouse_pos = mouse.x
                cur_mouse_pos = cur_mouse_pos - prev_mouse_pos_x
                prev_mouse_pos_x = mouse.x
                dhmx_recon.scale += cur_mouse_pos / 1024
            }
        }
    }


    Button {
        id: button_save
        objectName: "button_save"
        x: 38
        y: 869
        text: qsTr("Save to CFG")
    }

    Button {
        id: button_load
        objectName: "button_load"
        x: 144
        y: 869
        text: qsTr("Load From CFG")
    }

    Button {
        signal qml_signal_close
        id: button_cancel
        x: 534
        y: 869
        text: qsTr("Close")

        onClicked: {
            dhmx_recon.visible = false
            qml_signal_close()
        }
    }




    Item {
        id: prop_distance
        x: 38
        y: 101
        width: 620
        height: 160

        /* Propagation Distance */
        Label {
            id: label_prop
            x: 0
            y: 2
            text: qsTr("Propagation Distance (um)")
        }
        Slider {
            id: slider_prop_1
            objectName: "slider_prop_1"
            y: 25
            height: 40
            from: -255
            anchors.right: parent.right
            anchors.rightMargin: 205
            anchors.left: parent.left
            anchors.leftMargin: 0
            wheelEnabled: true
            stepSize: 0.01
            to: 255
            value: 0
            snapMode: Slider.SnapAlways
            onValueChanged: {
                spinBox_prop_1.value = slider_prop_1.value * spinBox_prop_1.factor
            }

            onPressedChanged: {
                console.log("slider_1 press changed")
                /* Send command only on release */
                if(!pressed){
                    if(spinBox_num_dist.value == 1)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                    if(spinBox_num_dist.value == 2)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                    if(spinBox_num_dist.value == 3)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
                    //purposely call session telemetry to tell DHMx to update the number of wavelengths.
                    //pack_cmd("session")
                }
            }
        }
        DoubleSpinBox {
            id: spinBox_prop_1
            objectName: "spinBox_prop_1"
            x: 431
            y: 25
            width: 189
            height: 40
            decimals: 6//3
            anchors.right: parent.right
            anchors.rightMargin: 0
            realValue: 0
            realFrom: -255
            realStepSize: 0.010
            realTo: 255.00
            realEdit: true

//            MouseArea{
//                id: clicky
//                anchors.fill: parent

//                onClicked: {
//                }
//            }

            Keys.onPressed: {
                send_cmd()
            }


            onValueModified: {
                slider_prop_1.value = spinBox_prop_1.realValue
                if(containsMouse){
                    send_cmd()
                }
            }
            function send_cmd(){
                if(spinBox_num_dist.value == 1)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                if(spinBox_num_dist.value == 2)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                if(spinBox_num_dist.value == 3)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
                //purposely call session telemetry to tell DHMx to update the number of wavelengths.
               // pack_cmd("session")
            }
        }

        Slider {
            id: slider_prop_2
            objectName: "slider_prop_2"
            x: 7
            y: 71
            height: 40
            from: -255
            to: 255
            anchors.left: parent.left
            value: 0
            wheelEnabled: true
            stepSize: 0.01
            anchors.right: parent.right
            anchors.rightMargin: 205
            anchors.leftMargin: 0
            onValueChanged: {
                   spinBox_prop_2.value = slider_prop_2.value * spinBox_prop_2.factor
            }

            onPressedChanged: {
                /* Send command only on release */
                if(!pressed){
                    if(spinBox_num_dist.value == 1)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                    if(spinBox_num_dist.value == 2)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                    if(spinBox_num_dist.value == 3)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
                    //purposely call session telemetry to tell DHMx to update the number of wavelengths.
                    //pack_cmd("session")
                }
            }
        }

        DoubleSpinBox {
            id: spinBox_prop_2
            objectName: "spinBox_prop_2"
            x: 431
            y: 71
            width: 189
            height: 40
            decimals: 6
            realValue: 0
            realFrom: -255
            realStepSize: 0.01
            realEdit: true
            anchors.right: parent.right
            anchors.rightMargin: 0
            realTo: 255

            Keys.onPressed: {
                send_cmd()
            }

            onValueModified: {
                slider_prop_2.value = spinBox_prop_2.realValue
                if(containsMouse){
                    send_cmd()
                }
            }
            function send_cmd(){
                if(spinBox_num_dist.value == 1)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                if(spinBox_num_dist.value == 2)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                if(spinBox_num_dist.value == 3)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
            }
        }

        Slider {
            id: slider_prop_3
            objectName: "slider_prop_3"
            x: 10
            y: 117
            height: 40
            from: -255
            to: 255
            anchors.left: parent.left
            value: 0
            wheelEnabled: true
            stepSize: 0.01
            anchors.right: parent.right
            anchors.leftMargin: 0
            anchors.rightMargin: 205

            onValueChanged: {
                   spinBox_prop_3.value = slider_prop_3.value * spinBox_prop_3.factor
            }

            onPressedChanged: {
                /* Send command only on release */
                if(!pressed){
                    if(spinBox_num_dist.value == 1)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                    if(spinBox_num_dist.value == 2)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                    if(spinBox_num_dist.value == 3)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
                }
            }

        }

        DoubleSpinBox {
            id: spinBox_prop_3
            objectName: "spinBox_prop_3"
            x: 431
            y: 117
            width: 189
            height: 40
            decimals: 6
            realValue: 0
            realStepSize: 0.01
            realFrom: -255
            realEdit: true
            anchors.right: parent.right
            anchors.rightMargin: 0
            realTo: 255

            Keys.onPressed: {
                send_cmd()
            }
            onValueModified: {
                slider_prop_3.value = spinBox_prop_3.realValue
                if(containsMouse){
                    send_cmd()
                }
            }
            function send_cmd(){
                if(spinBox_num_dist.value == 1)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                if(spinBox_num_dist.value == 2)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                if(spinBox_num_dist.value == 3)
                    pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
            }
        }
    }

    Item {
        id: chromatic_shift
        x: 40
        y: 272
        width: 620
        height: 114

        Label {
            id: label_chrom_shift
            x: 0
            y: 2
            text: qsTr("Chromatic Shift (um)")
        }

        /* Chromatic Shift 1 */
        Slider {
            id: slider_chrom_shift_1
            objectName: "slider_chrom_shift_1"
            y: 25
            height: 40
            from: -255
            anchors.right: parent.right
            anchors.rightMargin: 157
            anchors.left: parent.left
            anchors.leftMargin: 0
            value: 0
            stepSize: 0.01
            wheelEnabled: true
            to: 255
            onValueChanged: {
                spinBox_chrom_shift_1.vaue = slider_ctoStringhrom_shift_1.value * spinBox_chrom_shift_1.factor
            }
            onPressedChanged: {
                /* Send command only on release */
                if(!pressed){
                   pack_cmd("reconst chromatic_shift=["+metric_conversion(spinBox_chrom_shift_1.realValue,"um","m")+","+metric_conversion(spinBox_chrom_shift_2.realValue,"um","m")+"]")
                }
            }
        }
        DoubleSpinBox {
            id: spinBox_chrom_shift_1
            objectName: "spinBox_chrom_shift_1"
            x: 282
            y: 25
            decimals: 3
            realValue: 0
            realStepSize: 1
            realFrom: -255
            realTo: 255
            realEdit: true
            anchors.right: parent.right
            anchors.rightMargin: 0
            editable: true
            Keys.onPressed: {
                send_cmd()
            }
            onValueModified: {
                slider_chrom_shift_1.value = spinBox_chrom_shift_1.realValue
                if(containsMouse)
                   send_cmd()
            }
            function send_cmd(){
                pack_cmd("reconst chromatic_shift=["+metric_conversion(spinBox_chrom_shift_1.realValue,"um","m")+","+metric_conversion(spinBox_chrom_shift_2.realValue,"um","m")+"]")
            }

        }


        /* Chromatic Shift 2 */
        Slider {
            id: slider_chrom_shift_2
            objectName: "slider_chrom_shift_2"
            y: 71
            height: 40
            from: -255
            anchors.right: parent.right
            anchors.rightMargin: 157
            anchors.left: parent.left
            anchors.leftMargin: 0
            stepSize: 0.01
            value: 0
            wheelEnabled: true
            to: 255
            onValueChanged: {
                spinBox_chrom_shift_2.value = slider_chrom_shift_2.value * spinBox_chrom_shift_2.factor
            }
            onPressedChanged: {
                /* Send command only on release */
                if(!pressed){
                    pack_cmd("reconst chromatic_shift=["+metric_conversion(spinBox_chrom_shift_1.realValue,"um","m")+","+metric_conversion(spinBox_chrom_shift_2.realValue,"um","m")+"]")
                }
            }
        }
        DoubleSpinBox {
            id: spinBox_chrom_shift_2
            objectName: "spinBox_chrom_shift_2"
            x: 480
            y: 71
            decimals: 3
            realValue: 0
            realStepSize: 1
            realFrom: -255
            realTo: 255
            realEdit: true
            anchors.right: parent.right
            anchors.rightMargin: 0
            editable: true
            Keys.onPressed: {
                send_cmd()
            }
            onValueModified: {
                slider_chrom_shift_2.value = spinBox_chrom_shift_2.realValue
                if(containsMouse)
                   send_cmd()

            }
            function send_cmd(){
                pack_cmd("reconst chromatic_shift=["+metric_conversion(spinBox_chrom_shift_1.realValue,"um","m")+","+metric_conversion(spinBox_chrom_shift_2.realValue,"um","m")+"]")
            }
        }
    }

    Button {
        signal qml_signal_undo()
        id: button_undo
        objectName: "button_undo"
        x: 271
        y: 869
        text: qsTr("Undo Changes")
        onClicked: {
            qml_signal_undo()
        }
    }

    Label {
        id: label_title
        x: 38
        y: 25
        text: qsTr("Reconstruction Parameters")
        font.pointSize: 18
    }




    TabBar{
        id: bar
        x: 38
        y: 392
        width: 620
        height: 404
        currentIndex: 0

        TabButton{
            text: qsTr("Fitting")
        }
        TabButton{
            text: qsTr("Reference Hologram")
        }
        TabButton{
            text: qsTr("Region of Interest")
        }

        TabButton{
            text: qsTr("Phase")
        }
    }

    StackLayout{
        id: layout
        x: -73
        y: -128
        currentIndex: bar.currentIndex


        Item{
            id: tab1

            Rectangle{
                id:bg_tab1
                color: "#fbfbfb"

                x: 111
                y: 560

                width: 620
                height: 364

            }

            RadioDelegate {
                id: radio_t1_1d_seg
                objectName: "radio_t1_1d_seg"
                x: 372
                y: 587
                text: qsTr("1D Segments")
                enabled: false
                onCheckedChanged: {
                    if(containsMouse){
                        //pack_cmd("reconst fitting_mode=1d_sgment")
                    }
                }
            }

            ComboBox {
                id: comboBox_t1_1d_seg
                x: 517
                y: 593
                width: 187
                height: 40
                enabled: false
                displayText: "-- Fitting Method --"
                flat: false
            }

            RadioDelegate {
                id: radio_t1_2d_seg
                objectName: "radio_t1_2d_seg"
                x: 372
                y: 640
                text: qsTr("2D Segments")
                enabled: false
                onCheckedChanged: {
                    if(containsMouse){
                   //     pack_cmd("reconst fitting_mode=1d_sgment")
                    }
                }
            }

            ComboBox {
                id: comboBox_t1_2d_seg
                x: 517
                y: 646
                width: 187
                height: 40
                enabled: false
                displayText: "-- Fitting Method --"
            }

            SpinBox {
                id: spinBox_t1_fit_order
                x: 517
                y: 697
                width: 187
                height: 40
                enabled: false
                to: 9999
                onValueChanged: {
                    if(containsMouse)
                       pack_cmd("reconst fitting_order="+spinBox_t1_fit_order.value)
                }
            }

            Label {
                id: label_t1_fit_order
                x: 448
                y: 709
                color: "#a3a4a5"
                text: qsTr("Fit Order")
            }

            Button {
                id: button_t1_perform_fit
                x: 604
                y: 754
                text: qsTr("Perform Fit")
                enabled: false
                onClicked: {
                    //if no radio button is selected, create a popup and notify user
                    if(!radio_t1_1d_seg.checked && !radio_t1_2d_seg.checked){
                        popup_dhmxRecon.popupText = "Please select either 1D or 2D segments before applying."
                        popup_dhmxRecon.open()
                    }
                    if(radio_t1_1d_seg.checked){
                        pack_cmd("reconst fitting_mode=1d_segment")//in the future fitting_mode=TBD
                    }
                    if(radio_t1_2d_seg.checked){
                        pack_cmd("reconst fitting_mode=2d_segment")//in the future fitting_mode=TBD
                    }
                }
            }

            Button {
                id: button_t1_reset
                x: 156
                y: 754
                text: qsTr("Reset Phase Mask")
                onClicked: {
                    pack_cmd("reconst reset_phase_mask=true")
                }
            }

            Item{
                CheckDelegate {
                    id: radio_t1_max_val
                    objectName: "radio_t1_max_val"
                    x: 133
                    y: 590
                    text: qsTr("Maximum Value")
                    checked: false
                    onClicked: {
                        if(containsMouse){
                            pack_cmd("reconst center_max_value=True")
                        }
                        else{
                            pack_cmd("reconst center_max_value=False")
                        }
                    }
                }

                CheckDelegate {
                    id: radio_t1_wide_spec
                    objectName: "radio_t1_wide_spec"
                    x: 137
                    y: 639
                    text: qsTr("Wide Spectrum")
                    checked: false
                    onClicked: {
                        if(containsMouse){
                            pack_cmd("reconst center_wide_spectrum=True")
                        }
                        else{
                            pack_cmd("reconst center_wide_spectrum=False")
                        }
                    }
                }
            }

            Button {
                id: button_t1_center
                objectName: "button_t1_center"
                x: 448
                y: 852
                text: qsTr("Center Image")
                onClicked: {
                    pack_cmd("reconst center_image=yes")
                }
            }

            Button {
                id: button_t1_center_tilt
                objectName: "button_t1_center_tilt"
                x: 570
                y: 852
                text: qsTr("Center Image + Tilt")
                onClicked: {
                    pack_cmd("reconst center_image_and_tilt=yes")
                }
            }

            Button {
                id: button_t1_compute_spectral_peak
                objectName: "button_t1_compute_spectral_peak"
                x: 127
                y: 698
                text: qsTr("Compute Spectral Peak")
                onClicked: {
                    pack_cmd("reconst compute_spectral_peak=true")
                }
            }

        }
        Item{
            id: tab2

            Rectangle{
                id:bg_tab2
                color: "#fbfbfb"

                x: 111
                y: 560

                width: 620
                height: 364

                CheckBox {
                    id: check_t2_use_ref
                    objectName: "check_t2_use_ref"
                    x: 23
                    y: 92
                    text: qsTr("Use Reference Hologram")
                    onCheckedChanged: {
                        if(containsMouse){
                            if(check_t2_use_ref.checked){
                                pack_cmd("reconst ref_holo_enable=yes")
                                enable_t2()
                            }
                            else{
                                pack_cmd("reconst ref_holo_enable=no")
                                disable_t2()
                            }
                        }
                    }
                    Component.onCompleted: {
                        if(check_t2_use_ref.checked){
                            enable_t2()
                        }
                        else{
                            disable_t2()
                        }
                    }
                }

                Button {
                    id: button_t2_cur_holo
                    x: 23
                    y: 185
                    text: qsTr("Use Current Hologram")
                }

                DoubleSpinBox {
                    id: spinBox_t2_avg
                    objectName: "spinBox_t2_avg"
                    x: 419
                    y: 92
                    width: 126
                    height: 40
                    enabled: false
                    realEdit: true
                    realTo: 9999
                    ToolTip.visible: hovered
                    ToolTip.delay: 1000
                    ToolTip.text: "Frames per match"
                    Keys.onPressed: {
                        send_cmd()
                    }
                    onValueChanged: {
                        if(containsMouse)
                           send_cmd()
                    }
                    function send_cmd(){
                        pack_cmd("reconst ref_holo_averaging_sec="+spinBox_t2_avg.value/100)
                    }
                }

                CheckBox {
                    id: check_t2_avg
                    objectName: "check_t2_avg"
                    x: 298
                    y: 92
                    text: qsTr("Averaging")
                    ToolTip.visible: hovered
                    ToolTip.delay: 1000
                    ToolTip.text: "Frames per match"
                    onCheckedChanged: {
                        if(containsMouse){
                           if(check_t2_avg.checked){
                               spinBox_t2_avg.enabled = true
                               pack_cmd("reconst averaging_enable=yes")
                               pack_cmd("reconst ref_holo_averaging_sec="+spinBox_t2_avg.value)
                           }
                           else{
                               spinBox_t2_avg.enabled = false
                               pack_cmd("reconst averaging_enable=no")
                           }
                        }
                    }
                }

                Button {
                    id: button_t2_new_holo
                    x: 23
                    y: 238
                    width: 168
                    height: 40
                    text: qsTr("Load New Hologram")
                    onClicked:{
                        dhmx_fd.nameFilters = ["Tif files (*.tif)","All files (*)"]
                        open_file_dialog("Select a Reference Hologram","reconst ref_holo_path=",false,false)
                    }
                }

                TextField {
                    id: textField_holo
                    objectName: "textField_holo"
                    x: 198
                    y: 238
                    width: 391
                    height: 40
                    text: qsTr("")
                    placeholderText: "Please select a file..."
                }

                Button {
                    id: button_t2_save
                    x: 23
                    y: 293
                    width: 168
                    height: 40
                    text: qsTr("Save")
                }

                Label {
                    id: label_t2_sec
                    x: 552
                    y: 104
                    text: qsTr("sec.")
                }

            }
        }

        Item{
            id: tab3

            Rectangle{
                id:bg_tab3
                color: "#fbfbfb"

                x: 111
                y: 560

                width: 620
                height: 364

            }


            SpinBox {
                id: spinBox_t3_offset_x
                objectName: "spinBox_t3_offset_x"
                x: 310
                y: 632
                to: 9999
                editable: true
                Keys.onPressed: {
                    send_cmd()
                }
                onValueChanged: {
                       if(containsMouse)
                          send_cmd()
                }
                function send_cmd(){
                    pack_cmd("reconst roi_offset_x="+spinBox_t3_offset_x.value)
                }

            }

            SpinBox {
                id: spinBox_t3_size_x
                objectName: "spinBox_t3_size_x"
                x: 310
                y: 688
                to: 9999
                editable: true
                Keys.onPressed: {
                    send_cmd()
                }
                onValueChanged: {
                    if(containsMouse)
                       send_cmd()
                }
                function send_cmd(){
                    pack_cmd("reconst roi_size_x="+spinBox_t3_size_x.value)
                }
            }


            SpinBox {
                id: spinBox_t3_offset_y
                objectName: "spinBox_t3_offset_y"
                x: 510
                y: 632
                to: 9999
                editable: true
                Keys.onPressed: {
                    send_cmd()
                }
                onValueChanged: {
                    if(containsMouse)
                       send_cmd()
                }
                function send_cmd(){
                    pack_cmd("reconst roi_offset_y="+spinBox_t3_offset_y.value)
                }
            }
            SpinBox {
                id: spinBox_t3_size_y
                objectName: "spinBox_t3_size_y"
                x: 510
                y: 688
                to: 9999
                editable: true
                Keys.onPressed: {
                    send_cmd()
                }
                onValueChanged: {
                    if(containsMouse)
                       send_cmd()

                }
                function send_cmd(){
                    pack_cmd("reconst roi_size_y="+spinBox_t3_size_y.value)
                }
            }

            Label {
                id: label_t3_offset
                x: 186
                y: 644
                text: qsTr("Offset")
            }

            Label {
                id: label_t3_size
                x: 203
                y: 700
                text: qsTr("Size")
            }

            Label {
                id: label_t3_x
                x: 375
                y: 594
                text: qsTr("X")
            }

            Label {
                id: label_t3_y
                x: 575
                y: 594
                text: qsTr("Y")
            }

            Button {
                id: button4
                x: 370
                y: 839
                text: qsTr("Reset")
                onClicked: {
                    reset_size_and_offsets()
                }
            }

            Label {
                id: label_t3_px
                x: 456
                y: 644
                text: qsTr("px")
            }

            Label {
                id: label_t3_px1
                x: 456
                y: 700
                text: qsTr("px")
            }

            Label {
                id: label_t3_px2
                x: 656
                y: 700
                text: qsTr("px")
            }

            Label {
                id: label_t3_px3
                x: 656
                y: 644
                text: qsTr("px")
            }
        }
        Item{
            id: tab4

            Rectangle{
                id:bg_tab4
                color: "#fbfbfb"

                x: 111
                y: 560

                width: 620
                height: 364

                ComboBox {
                    id: comboBox_t4_alg
                    objectName: "comboBox_t4_alg"
                    x: 22
                    y: 110
                    width: 403
                    height: 40
                    enabled: false
                    displayText: "-- Please Select a Phase Unwrapping Algorithm --"
                    model: ListModel{
                        id: model_alg
                        ListElement{
                            text: "Algorithm 1"
                        }
                        ListElement{
                            text: "Algorithm 2"
                        }
                        ListElement{
                            text: "Algorithm 3"
                        }
                    }
                }

                CheckBox {
                    id: check_t4_unwrap
                    objectName: "check_t4_unwrap"
                    enabled: false
                    x: 484
                    y: 110
                    text: qsTr("Unwrap")
                    onCheckedChanged: {
                        if(check_t4_unwrap.checked){
                            comboBox_t4_alg.enabled = true
                            pack_cmd("reconst phase_unwrapping_enable=yes")
                        }
                        else{
                            comboBox_t4_alg.enabled = false
                            pack_cmd("reconst phase_unwrapping_enable=no")
                        }
                    }
                }

            }
        }


    }

    SpinBox {
        id: spinBox_num_dist
        objectName: "spinBox_num_dist"
        x: 518
        y: 62
        to: 3
        value: 0
        onValueChanged:{
            update_prop_distances()

                /* Send command only on release */
                if(!clicked){
                    if(spinBox_num_dist.value == 1)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+"]")
                    if(spinBox_num_dist.value == 2)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+"]")
                    if(spinBox_num_dist.value == 3)
                       pack_cmd("reconst propagation_distance=["+spinBox_prop_1.realValue+","+spinBox_prop_2.realValue+","+spinBox_prop_3.realValue+"]")
                    //purposely call session telemetry to tell DHMx to update the number of wavelengths.
                    pack_cmd("session")
                }


        }
    }

    Label {
        id: label_num_dist
        x: 38
        y: 73
        text: qsTr("Number of Distances")
    }

    onVisibleChanged: {
        update_prop_distances()
    }


   DhmxPopup {
       id:popup_dhmxRecon
       parent: Overlay.overlay
       //TODO: Fix positioning system.  For some reason the x values get really huge and the popup window does not know how to track
       //Must be a DPI problem with large monitors.
       xPos: dhmx_recon.x/2 + ((dhmx_recon.width - popup_dhmxRecon.width)/2)
       yPos: dhmx_recon.y/2 + ((dhmx_recon.height - popup_dhmxRecon.height)/2)
   }

   FileDialog{
       signal qml_signal_send_file_path(string path, string cmd)
       id: dhmx_fd
       objectName: "dhmx_fd"
       title: "DEFAULT"
       //folder: shortcuts.home
       nameFilters: ["Image files (*.jpg *.png *.bmp *.tif)","All files (*)"]

       property string cmd_type: ""

       onAccepted: {
           var path = dhmx_fd.fileUrl.toString();
           var cleanPath
           path = path.replace(/^(file:\/{2})/,"");
           cleanPath = decodeURIComponent(path);
           pack_cmd(cmd_type+cleanPath)

           //Specific just for this window
           textField_holo.text = cleanPath

       }
       onRejected: {
           dhmx_fd.close()
       }
       Component.onCompleted: visible = false
   }


   /* This function opens a file dialog window but also passes in a command so that in the
    * PyQt side, the command is structured and sent */
   /* example: open_file_dialog('/home/qt','Please Select a File','framesource mode=') */
   function open_file_dialog(title,cmd_type,one_or_many,select_folder){
       dhmx_fd.setSelectMultiple(one_or_many)
       dhmx_fd.setSelectFolder(select_folder)
       dhmx_fd.title = title
       dhmx_fd.cmd_type = cmd_type
       dhmx_fd.open()
   }

    /* Functions to change visibility and sensitivity of fields (n-1) */
    function update_prop_distances(){
        if(spinBox_num_dist.value == "1"){
            spinBox_prop_1.enabled = true
            slider_prop_1.enabled = true

            spinBox_prop_2.enabled = false
            slider_prop_2.enabled = false

            spinBox_prop_3.enabled = false
            slider_prop_3.enabled = false
        }
        if(spinBox_num_dist.value == "2"){
            spinBox_prop_1.enabled = true
            slider_prop_1.enabled = true

            spinBox_prop_2.enabled = true
            slider_prop_2.enabled = true

            spinBox_prop_3.enabled = false
            slider_prop_3.enabled = false
        }
        if(spinBox_num_dist.value == "3"){
            spinBox_prop_1.enabled = true
            slider_prop_1.enabled = true

            spinBox_prop_2.enabled = true
            slider_prop_2.enabled = true

            spinBox_prop_3.enabled = true
            slider_prop_3.enabled = true
        }
    }
    function reset_size_and_offsets(){
        spinBox_t3_offset_x.value = 0
        spinBox_t3_offset_y.value = 0
        spinBox_t3_size_x.value = 2048
        spinBox_t3_size_y.value = 2048
    }

    function set_mouse_starting_pos_x(){
        starting_mouse_pos_x = mouseX

    }

    function get_mouse_distance_x(){
        return 1.0
    }

    function remap(num, in_min, in_max, out_min, out_max){
        return (num - in_min) * (out_max - out_min) / (in_max - in_min) +out_min
    }

    function enable_t2(){
        button_t2_cur_holo.enabled = true
        button_t2_new_holo.enabled = true
        button_t2_save.enabled = true
        check_t2_avg.enabled = true
        spinBox_t2_avg.enabled = true
        textField_holo.enabled = true
    }
    function disable_t2(){
        button_t2_cur_holo.enabled = false
        button_t2_new_holo.enabled = false
        button_t2_save.enabled = false
        check_t2_avg.enabled = false
        spinBox_t2_avg.enabled = false
        textField_holo.enabled = false

    }
    function metric_conversion(item, scale_in, scale_out){
        var scale_factor = 0
        //var item_output = parseInt(item,10)
        var item_output = item

        if(scale_in == "nm" && scale_out == "m"){
            scale_factor = 1e-9
        }
        if(scale_in == "um" && scale_out == "m"){
            scale_factor = 1e-6
        }
        if(scale_in == "mm" && scale_out == "m"){
            scale_factor = 1e-2
        }

        if(scale_in == "m" && scale_out == "mm"){
            scale_factor = 1e2
        }
        if(scale_in == "m" && scale_out == "um"){
            scale_factor = 1e6
        }
        if(scale_in = "m" && scale_out == "nm"){
            scale_factor = 1e9
        }

        return (item_output * scale_factor).toPrecision(6)
    }
}




