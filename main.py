from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from data import *
from materias import *

currTimetable = 0

app = QApplication([])

window = QWidget()
window.setGeometry(350,150,1200,800)
window.setLayout(QGridLayout())
window.setWindowTitle("Generador de Horarios FC 2021-2")

splitter = QSplitter()
window.layout().addWidget(splitter)

leftSection = QWidget()
rightSection = QWidget()

leftSection.setLayout(QGridLayout())
rightSection.setLayout(QGridLayout())

lista = QTreeWidget()
lista.setHeaderLabel("Selecciona los grupos que deseas tomar en cuenta")

for plan in carreras:
    planItem = QTreeWidgetItem()
    planItem.setText(0, plan)
    for semestre in carreras[plan]:
        semestreItem = QTreeWidgetItem()
        semestreItem.setText(0, semestre)
        semestreItem.setCheckState(0, Qt.Unchecked)
        semestreItem.setFlags(Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        planItem.addChild(semestreItem)
        for materia in carreras[plan][semestre]:
            materiaItem = QTreeWidgetItem()
            materiaItem.setText(0, materia)
            materiaItem.setCheckState(0, Qt.Unchecked)
            semestreItem.addChild(materiaItem)
            materiaItem.setFlags(Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            for grupo in carreras[plan][semestre][materia]:
                grupoItem = QTreeWidgetItem()
                grupoItem.setText(0, grupo + ": " + carreras[plan][semestre][materia][grupo][0])
                grupoItem.setCheckState(0, Qt.Unchecked)
                materiaItem.addChild(grupoItem)
    lista.addTopLevelItem(planItem)

generarButton = QPushButton("Generar")
generarButton.setMinimumHeight(40)

validTimetables = []

def handleGeneration():
    global window
    global timetable
    global validTimetables
    global modelDias
    timetable.setEnabled(False)
    generarButton.setEnabled(False)
    nextHorarioButton.setEnabled(False)
    prevHorarioButton.setEnabled(False)
    lista.setEnabled(False)
    QApplication.processEvents()
    modelDias.clear()
    currTimetableLabel.setText("Generando:")
    timetable.setModel(modelDias)
    QApplication.processEvents()
    currTimetable = 0
    generador = generadorHorarios()
    prevGrupos = {}
    root = lista.invisibleRootItem()
    root_child_count = root.childCount()
    materias_count, grupos_count = 0, 0
    for a in range(root_child_count):
        plan = root.child(a)
        plan_child_count = plan.childCount()
        for b in range(plan_child_count):
            semestre = plan.child(b)
            semestre_child_count = semestre.childCount()
            for c in range(semestre_child_count):
                materia = semestre.child(c)
                materia_child_count = materia.childCount()
                for d in range(materia_child_count):
                    grupo = materia.child(d)
                    index = grupo.text(0).find(":")
                    grupoNum = grupo.text(0)[0:index]
                    if grupo.checkState(0) == Qt.Checked:
                        if not (grupoToMateria[grupoNum] in prevGrupos):
                            materias_count += 1
                            prevGrupos[grupoToMateria[grupoNum]] = {}
                        prevGrupos[grupoToMateria[grupoNum]][grupoNum] = grupoToTimetable[grupoNum]
                        grupos_count += 1
    currTimetableLabel.setText("Generando para " + str(grupos_count) + " grupos de " + str(materias_count) + " materias diferentes")
    QApplication.processEvents()
    horarios = []
    for materia in prevGrupos:
        grupos = {}
        for grupo in prevGrupos[materia]:
            grupos[grupo] = prevGrupos[materia][grupo]
        horarios.append(grupos.copy())
    generador.getTimetable(horarios,0,[],[])
    validTimetables = generador.validTimetables.copy()
    if validTimetables != [[]]:
        table = validTimetables[0]
        printTable(table)
        timetable.setEnabled(True)
        generarButton.setEnabled(True)
        nextHorarioButton.setEnabled(True)
        prevHorarioButton.setEnabled(True)
        lista.setEnabled(True)
    else:
        currTimetableLabel.setText("No existen combinaciones")
        lista.setEnabled(True)
        generarButton.setEnabled(True)

generarButton.clicked.connect(handleGeneration)

leftSection.layout().addWidget(lista, 0, 0)
leftSection.layout().addWidget(generarButton, 2, 0)

timetable = QTableView()
timetable.setEnabled(False)
timetable.setLayout(QGridLayout())
timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
timetable.verticalHeader().setDefaultSectionSize(40)

modelDias = QStandardItemModel()
dias = ["L","Ma","Mi","J","V","S"]

timetable.setModel(modelDias)
timetable.clearSpans()

def printTable(table):
    modelDias.clear()
    for i in range(0,6):
        modelDias.setHorizontalHeaderItem(i,QStandardItem(dias[i]))

    for i in range(25200,25200 + 54000, 1800):
        modelDias.setVerticalHeaderItem((i-25200)//60//30, QStandardItem(num_to_time(i) + " - " + num_to_time(i+1800)))
    tabla = getPrintableTimetable(table, grupoToTimetable)
    for i in range(0,6):
        for j in range(len(tabla[i])):
            if tabla[i][j][0] + 1:
                grupoo = tabla[i][j][2]
                modelDias.setItem(tabla[i][j][0], i, QStandardItem(grupoToMateria[grupoo] + "\n" + grupoToProfesor[grupoo]))
                modelDias.item(tabla[i][j][0], i).setEditable(False)
                timetable.setSpan(tabla[i][j][0], i, tabla[i][j][1],1)
    currTimetableLabel.setText(str(currTimetable+1) + "/" + str(len(validTimetables)))
    timetable.setModel(modelDias)
    timetable.resizeRowsToContents()

nextHorarioButton = QPushButton("Siguiente")
nextHorarioButton.setEnabled(False)
prevHorarioButton = QPushButton("Anterior")
prevHorarioButton.setEnabled(False)
currTimetableLabel = QLabel("")
rightSection.layout().addWidget(nextHorarioButton, 0, 2)
rightSection.layout().addWidget(currTimetableLabel, 0, 1, Qt.AlignHCenter)
rightSection.layout().addWidget(prevHorarioButton, 0, 0)
rightSection.layout().addWidget(timetable, 1, 0, 1, 3)

def handleNextHorario():
    global currTimetable
    currTimetable = (currTimetable + 1) % len(validTimetables)
    printTable(validTimetables[currTimetable])

def handlePrevHorario():
    global currTimetable
    currTimetable = currTimetable - 1
    if currTimetable < 0:
        currTimetable = len(validTimetables) - 1
    else:
        currTimetable = currTimetable % len(validTimetables)
    printTable(validTimetables[currTimetable])

nextHorarioButton.clicked.connect(handleNextHorario)
prevHorarioButton.clicked.connect(handlePrevHorario)

splitter.insertWidget(0,leftSection)
splitter.insertWidget(1,rightSection)
splitter.setSizes([400,800])
timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

window.show()
app.exec_()
