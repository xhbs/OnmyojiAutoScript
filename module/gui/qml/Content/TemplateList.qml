import QtQuick
import QtQuick.Layouts
import FluentUI
import '../Global'

Item{
    id: root

    ListModel{
        id: templateModel
    }

    ListModel{
        id: taskModel
    }

    FluScrollablePage{
        anchors.fill: parent
        leftPadding: 12
        rightPadding: 12
        topPadding: 12
        bottomPadding: 12
        spacing: 10

        FluText{
            text: qsTr("Template Management")
            font: FluTextStyle.Title
            Layout.fillWidth: true
        }

        RowLayout{
            Layout.fillWidth: true
            spacing: 8

            FluTextBox{
                id: templateName
                Layout.fillWidth: true
                placeholderText: qsTr("Template name")
            }

            FluButton{
                text: qsTr("New")
                onClicked: clearEditor()
            }

            FluFilledButton{
                text: qsTr("Save")
                onClicked: saveCurrentTemplate()
            }

            FluButton{
                text: qsTr("Delete")
                onClicked: deleteCurrentTemplate()
            }
        }

        FluText{
            text: qsTr("Templates")
            font: FluTextStyle.BodyStrong
            Layout.fillWidth: true
        }

        FluArea{
            Layout.fillWidth: true
            implicitHeight: templateColumn.implicitHeight + 20

            ColumnLayout{
                id: templateColumn
                anchors{
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    margins: 10
                }
                spacing: 8

                Repeater{
                    model: templateModel
                    delegate: Item{
                        Layout.fillWidth: true
                        implicitHeight: 44

                        FluText{
                            anchors.left: parent.left
                            anchors.right: editButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: model.name + "  (" + taskSummary(model.tasks_json) + ")"
                            elide: Text.ElideRight
                        }

                        FluButton{
                            id: editButton
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Edit")
                            onClicked: editTemplate(index)
                        }
                    }
                }
            }
        }

        FluText{
            text: qsTr("Select tasks for this template")
            font: FluTextStyle.BodyStrong
            Layout.fillWidth: true
        }

        FluArea{
            Layout.fillWidth: true
            implicitHeight: taskColumn.implicitHeight + 20

            ColumnLayout{
                id: taskColumn
                anchors{
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    margins: 10
                }
                spacing: 4

                Repeater{
                    model: taskModel
                    delegate: FluCheckBox{
                        Layout.fillWidth: true
                        text: qsTranslate("TaskList", model.task)
                        selected: model.enabled
                        clickFunc: function(){
                            selected = !selected
                            taskModel.setProperty(index, "enabled", selected)
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: reload()

    function reload(){
        loadTasks()
        loadTemplates()
        clearEditor()
    }

    function loadTasks(){
        taskModel.clear()
        const data = JSON.parse(process_manager.gui_task_list(MainEvent.scriptName))
        const menu = JSON.parse(process_manager.gui_menu())
        for(const group in menu){
            if(group === "Overview" || group === "TaskList" || group === "Script" || group === "Tools"){
                continue
            }
            for(const task of menu[group]){
                if(task in data){
                    taskModel.append({"task": task, "enabled": data[task]["enable"]})
                }
            }
        }
    }

    function loadTemplates(){
        templateModel.clear()
        const data = JSON.parse(template_manager.list_templates())
        for(const item of data){
            templateModel.append(item)
        }
    }

    function clearEditor(){
        templateName.text = ""
        for(var i = 0; i < taskModel.count; i++){
            taskModel.setProperty(i, "enabled", false)
        }
    }

    function editTemplate(index){
        const item = templateModel.get(index)
        const tasks = JSON.parse(item.tasks_json)
        templateName.text = item.name
        for(var i = 0; i < taskModel.count; i++){
            taskModel.setProperty(i, "enabled", tasks.indexOf(taskModel.get(i).task) >= 0)
        }
    }

    function taskSummary(tasksJson){
        const tasks = JSON.parse(tasksJson)
        var labels = []
        for(const task of tasks){
            labels.push(qsTranslate("TaskList", task))
        }
        return labels.join(", ")
    }

    function selectedTasks(){
        var result = []
        for(var i = 0; i < taskModel.count; i++){
            if(taskModel.get(i).enabled){
                result.push(taskModel.get(i).task)
            }
        }
        return result
    }

    function saveCurrentTemplate(){
        if(template_manager.save_template(templateName.text, JSON.stringify(selectedTasks()))){
            showSuccess(qsTr("Template saved"))
            loadTemplates()
        }else{
            showSuccess(qsTr("Template name and tasks are required"))
        }
    }

    function deleteCurrentTemplate(){
        if(template_manager.delete_template(templateName.text)){
            showSuccess(qsTr("Template deleted"))
            loadTemplates()
            clearEditor()
        }else{
            showSuccess(qsTr("Select a template to delete"))
        }
    }
}
