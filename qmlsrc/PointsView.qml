import QtQuick 2.0
import QtQuick.Controls 2.1

Page {
    id: root
    signal addPoint()
    property alias headerTitle: headerLabel.text
    property var model: []
    property var keys: []
    property string addPointText
    width: 400
    height: 400
    header: HeaderLabel {
        id: headerLabel
    }

    ListView {
        clip: true
        anchors.fill: parent
        header: Row {}
        delegate: Row {
            property int indexrow: index
            height: 40
            x: 8
            spacing: 8
            Row {
                Button {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 24
                    height: 24
                    text: "-"
                    onClicked: {
                        root.model.splice(indexrow, 1)
                        modelChanged()
                    }
                }

                spacing: 8
                Repeater {
                    delegate: Row {

                        Label {
                            text: modelData + " = "
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        TextField {
                            selectByMouse: true
                            text: root.model[indexrow][modelData]
                            width: 150
                            height: 32
                            anchors.verticalCenter: parent.verticalCenter
                            onTextChanged: {
                                root.model[indexrow][modelData] = text
                            }
                        }
                    }
                    model: keys
                }
            }
        }
        model: root.model

    }

    footer: Button {
        text: addPointText
        onClicked: addPoint()
    }
}
