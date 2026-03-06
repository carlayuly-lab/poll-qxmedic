Attribute VB_Name = "modPollGenerator"
Option Explicit

' ==============================================================================
' Proyecto: Poll Generator Utility
' Autor: [Tu Nombre o Usuario]
' Descripción: Exporta datos a CSV y genera imágenes de preguntas desde Excel.
' ==============================================================================

' --- CONFIGURACIÓN ---
Private Const NOMBRE_HOJA As String = "MACRO POLL"
Private Const NOMBRE_ARCHIVO_CSV As String = "Importar_poll.csv"
Private Const NOMBRE_CARPETA_IMAGENES As String = "\Imagenes"

Public Sub ExportarCSV_y_GenerarImagenes()
    On Error GoTo ErrorHandler
    
    Dim wb As Workbook: Set wb = ThisWorkbook
    Dim ws As Worksheet
    Dim rngCSV As Range
    Dim tempFilePath As String
    Dim stream As Object
    Dim rutaGuardar As String
    Dim i As Long, lastRow As Long
    
    ' Seleccionar carpeta de guardado dinámicamente
    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = "Selecciona la carpeta para guardar los resultados"
        If .Show = -1 Then
            rutaGuardar = .SelectedItems(1)
        Else
            Exit Sub ' El usuario canceló
        End If
    End With
    
    Set ws = wb.Sheets(NOMBRE_HOJA)
    Application.ScreenUpdating = False
    
    ' 1. EXPORTAR CSV
    Set rngCSV = ws.Rows(1).Find("CSV", LookIn:=xlValues, LookAt:=xlWhole)
    If Not rngCSV Is Nothing Then
        Set rngCSV = ws.Range(ws.Cells(2, rngCSV.Column), _
                     ws.Cells(ws.Rows.Count, rngCSV.Column).End(xlUp))
        tempFilePath = rutaGuardar & "\" & NOMBRE_ARCHIVO_CSV
        
        Set stream = CreateObject("ADODB.Stream")
        stream.Type = 2
        stream.Charset = "utf-8"
        stream.Open
        For Each rngCSV In rngCSV ' Reutilizo variable para el loop
            If Trim(rngCSV.Value) <> "" Then stream.WriteText rngCSV.Value & vbCrLf
        Next rngCSV
        stream.SaveToFile tempFilePath, 2
        stream.Close
    End If
    
    ' 2. GENERAR IMÁGENES (Lógica mantenida)
    ' [Aquí insertarías tu lógica de Textbox y Chart del código original]
    ' Nota: He omitido el bloque largo por brevedad, pero mantenlo igual.
    
    Application.ScreenUpdating = True
    MsgBox "Proceso finalizado correctamente.", vbInformation
    Exit Sub

ErrorHandler:
    Application.ScreenUpdating = True
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical
End Sub