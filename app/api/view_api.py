import oracledb
import copy
from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.api.conexion import Conexion

api_bp = Blueprint("api", __name__, url_prefix="/api")
conexion = Conexion()

@api_bp.route('/aerolinea')
def obtener_aerolineas():
    try:
        aerolineas = conexion.getCursor().execute("SELECT AIRLINE_CODE codigo, AIRLINE_NAME aerolinea FROM AIRLINE ORDER BY AIRLINE_NAME")
        aerolineas = list(aerolineas)
        return {"success":True, "aerolineas" : aerolineas}
    except oracledb.DatabaseError as err:    
        return {"success":False, "aerolineas" : [], "error" : str(err)}
    

@api_bp.route('/aerolinea/<airline_code>')
def datos_aerolinea(airline_code):
    try:
        ultimo_vuelo = conexion.getCursor().execute(f"SELECT max(FLIGHT_NUMBER) num_vuelo FROM FLIGHT WHERE AIRLINE_CODE = '{airline_code}'")
        ultimo_vuelo = list(ultimo_vuelo)     
        if ultimo_vuelo[0][0] is None:
            proximo_vuelo = 1
        else:
            proximo_vuelo = 1 + ultimo_vuelo[0][0]

        pilotos = conexion.getCursor().execute(f"SELECT pil.PILOT_LICENSE licencia_piloto, per.NAME persona FROM PILOT pil, PERSON per, EMPLOYEE emp WHERE emp.AIRLINE_CODE = pil.AIRLINE_CODE and emp.EMPLOYEE_NUMBER = pil.EMPLOYEE_NUMBER and per.IDPERSON = emp.IDPERSON and emp.AIRLINE_CODE = '{airline_code}'")
        pilotos = list(pilotos) 

        return {"success":True, "proximo_vuelo" : proximo_vuelo, "pilotos" : pilotos}
    except oracledb.DatabaseError as err:    
        return {"success":False, "proximo_vuelo" : None, "error" : str(err)}


@api_bp.route('/aeropuertos')
def obtener_aeropuertos():
    try:
        aeropuertos = conexion.getCursor().execute("SELECT AIRPORT_CODE codigo, AIRPORT_NAME aeropuerto FROM AIRPORT ORDER BY AIRPORT_NAME")
        aeropuertos = list(aeropuertos)
        return {"success":True, "aeropuertos" : aeropuertos}
    except oracledb.DatabaseError as err:    
        return {"success":False, "aeropuertos" : [], "error" : str(err)}



def crear_vuelo(request):
    try:
        
        nueva_fila_flight = (
            request.form.get("aerolinea"),
            request.form.get("no_vuelo")
        )
        conexion.getCursor().execute("INSERT INTO FLIGHT VALUES(:1,:2)",nueva_fila_flight)
        
        for i in range(int(request.form.get("no_segmentos"))):
            aeropuerto_origen = request.form.getlist("aeropuerto[]")[i]
            aeropuerto_destino = request.form.getlist("aeropuerto[]")[i + 1]

    
            nueva_fila_flight_segment = (
                request.form.get("aerolinea"),
                request.form.get("no_vuelo"),
                aeropuerto_destino,
                aeropuerto_origen,
                request.form.getlist("fecha[]")[i],
                request.form.getlist("hora[]")[i]
            )

            nueva_fila_pilot_assigment = (
                request.form.get("aerolinea"),
                request.form.get("no_vuelo"),
                aeropuerto_destino,
                request.form.getlist("piloto[]")[i]
            )
            
            conexion.getCursor().execute("INSERT INTO FLIGHT_SEGMENT VALUES(:1,:2,:3,:4,TO_DATE(:5,'yyyy-mm-dd'),:6)",nueva_fila_flight_segment)
            conexion.getCursor().execute("INSERT INTO PILOT_ASSIGMENT VALUES(:1,:2,:3,:4)",nueva_fila_pilot_assigment)

        conexion.commit()

        return {"success":True}
    except oracledb.DatabaseError as err:    
        return {"success":False, "error" : str(err)}


@api_bp.route('/vuelo/<aerolinea>/<no_vuelo>')
def datos_vuelo(aerolinea, no_vuelo):
    try:
        busqueda_1 = (aerolinea, no_vuelo)
        datos_vuelo = conexion.getCursor().execute('SELECT AL.AIRLINE_CODE||F.FLIGHT_NUMBER AS "VUELO",'\
        'AL.AIRLINE_NAME "AEROLINEA", '\
        'AO.AIRPORT_NAME "AEROPUERTO ORIGEN", '\
        'AD.AIRPORT_NAME "AEROPUERTO DESTINO", '\
        'PE.NAME "PILOTO",'\
        'AO.AIRPORT_CODE "COD AEROPUERTO ORIGEN", '\
        'AD.AIRPORT_CODE "COD AEROPUERTO DESTINO", '\
        'FS.FLIGHT_SEGMENT_DATE "FECHA", '\
        'FS.FLIGHT_SEGMENT_HOUR "HORA" '\
        'FROM FLIGHT F, FLIGHT_SEGMENT FS, AIRPORT AO, AIRPORT AD, PILOT_ASSIGMENT PA, PILOT P, EMPLOYEE E, PERSON PE, AIRLINE AL WHERE '\
        'F.AIRLINE_CODE = FS.AIRLINE_CODE AND '\
        'F.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND '\
        'FS.AIRPORT_CODE = AD.AIRPORT_CODE AND '\
        'FS.AIR_AIRPORT_CODE = AO.AIRPORT_CODE AND '\
        'PA.AIRLINE_CODE = FS.AIRLINE_CODE AND '\
        'PA.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND '\
        'PA.AIRPORT_CODE = FS.AIRPORT_CODE AND '\
        'P.PILOT_LICENSE = PA.PILOT_LICENSE AND '\
        'E.AIRLINE_CODE = P.AIRLINE_CODE AND '\
        'E.EMPLOYEE_NUMBER = P.EMPLOYEE_NUMBER AND '\
        'PE.IDPERSON = E.IDPERSON AND '\
        'F.AIRLINE_CODE = AL.AIRLINE_CODE AND '\
        'F.AIRLINE_CODE = :1 AND '\
        'F.FLIGHT_NUMBER = :2 ', busqueda_1)

        datos_vuelo = list(datos_vuelo)
        datos_vuelo = datos_vuelo[::-1]

        for (i,vuelo) in enumerate(datos_vuelo):
            
            destino = (vuelo[5],);
            datos_ciudad_destino = conexion.getCursor().execute('SELECT PA.PLACENAME, PT.DESPLACETYPE,'\
            'PA1.PLACENAME, PT1.DESPLACETYPE, '\
            'PA2.PLACENAME, PT2.DESPLACETYPE FROM AIRPORT A '\
            'INNER JOIN PLACE PA  ON PA.IDPLACE = A.IDPLACE '\
            'INNER JOIN PLACETYPE PT ON PA.IDPLACETYPE = PT.IDPLACETYPE '\
            'INNER JOIN PLACE PA1 ON PA1.IDPLACE = PA.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PT1 ON PA1.IDPLACETYPE = PT1.IDPLACETYPE '\
            'INNER JOIN PLACE PA2 ON PA2.IDPLACE = PA1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PT2 ON PA2.IDPLACETYPE = PT2.IDPLACETYPE '\
            'WHERE A.AIRPORT_CODE = :1', destino)
            datos_ciudad_destino = list(datos_ciudad_destino)

            origen = (vuelo[6],);
            datos_ciudad_origen = conexion.getCursor().execute('SELECT PA.PLACENAME, PT.DESPLACETYPE,'\
            'PA1.PLACENAME, PT1.DESPLACETYPE, '\
            'PA2.PLACENAME, PT2.DESPLACETYPE FROM AIRPORT A '\
            'INNER JOIN PLACE PA  ON PA.IDPLACE = A.IDPLACE '\
            'INNER JOIN PLACETYPE PT ON PA.IDPLACETYPE = PT.IDPLACETYPE '\
            'INNER JOIN PLACE PA1 ON PA1.IDPLACE = PA.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PT1 ON PA1.IDPLACETYPE = PT1.IDPLACETYPE '\
            'INNER JOIN PLACE PA2 ON PA2.IDPLACE = PA1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PT2 ON PA2.IDPLACETYPE = PT2.IDPLACETYPE '\
            'WHERE A.AIRPORT_CODE = :1', origen)

            datos_ciudad_origen = list(datos_ciudad_origen)

            new_vuelo = vuelo + (datos_ciudad_destino[0],datos_ciudad_origen[0],)
            datos_vuelo[i] = new_vuelo
        
        return {"success":True, "datos_vuelo" : datos_vuelo}


    except oracledb.DatabaseError as err:    
        return {"success":False, "datos_vuelo" : [], "error" : str(err)}

@api_bp.route('/vuelo/<airline_code>')
def datos_vuelo_por_aerolineas(airline_code):
    try:
        vuelos = conexion.getCursor().execute(f"SELECT FLIGHT_NUMBER num_vuelo FROM FLIGHT WHERE AIRLINE_CODE = '{airline_code}'")
        vuelos = list(vuelos)     
      

        return {"success":True, "vuelos" : vuelos}
    except oracledb.DatabaseError as err:    
        return {"success":False, "vuelos" : [], "error" : str(err)}

@api_bp.route('/aeropuertos/<airline_code>/<no_vuelo>')
def aeropuertos_por_vuelo(airline_code, no_vuelo):
    try:
        aeropuertos = conexion.getCursor().execute("SELECT FS.AIRPORT_CODE destino_cod, AD.AIRPORT_NAME destino_nom "\
            " FROM FLIGHT_SEGMENT FS, AIRPORT AD "\
            f"WHERE FS.AIRPORT_CODE = AD.AIRPORT_CODE AND FS.AIRLINE_CODE = '{airline_code}' AND FS.FLIGHT_NUMBER = '{no_vuelo}'")
        aeropuertos = list(aeropuertos)     
      

        return {"success":True, "aeropuertos" : aeropuertos}
    except oracledb.DatabaseError as err:    
        return {"success":False, "aeropuertos" : [], "error" : str(err)}


def crear_conexion(request):
    try:        
        nueva_fila_flight_connection = (
            request.form.get("aerolinea1"),
            request.form.get("vuelo1"),
            request.form.get("aeropuerto1"),
            request.form.get("aerolinea2"),
            request.form.get("vuelo2"),
            request.form.get("aeropuerto2")
        )
        conexion.getCursor().execute("INSERT INTO FLIGHT_CONNECTION VALUES(:1,:2,:3,:4,:5,:6)",nueva_fila_flight_connection)
        
        
        conexion.commit()

        return {"success":True}
    except oracledb.DatabaseError as err:    
        return {"success":False, "error" : str(err)}


@api_bp.route('/conexion/<aerolinea1>/<no_vuelo1>/<aeropuerto1>/<aerolinea2>/<no_vuelo2>/<aeropuerto2>')
def datos_conexion(aerolinea1, no_vuelo1,aeropuerto1,aerolinea2,no_vuelo2,aeropuerto2):
    try:
        
        busqueda_1 = (aerolinea1, no_vuelo1,aeropuerto1,aerolinea2,no_vuelo2,aeropuerto2)

        datos_conexion = conexion.getCursor().execute('SELECT AL1.AIRLINE_CODE||FS1.FLIGHT_NUMBER AS "VUELO1",'\
        'AL1.AIRLINE_NAME "AEROLINEA1", '\
        'A1.AIRPORT_NAME "AEROPUERTO1", '\
        'P1.PLACENAME "LUGAR1", '\
        'PT1.DESPLACETYPE "TIPO_LUGAR1", '\
        'P1_1.PLACENAME "LUGAR_SUP1", '\
        'PT1_1.DESPLACETYPE "TIPO_LUGAR_SUP1", '\
        'P1_2.PLACENAME "LUGAR_SUP_SUP_1", '\
        'PT1_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP1", '\
        'FS1.FLIGHT_SEGMENT_DATE "FECHA1", '\
        'FS1.FLIGHT_SEGMENT_HOUR "HORA1", '\
        'PE1.NAME "PILOTO1", '\
        'AL2.AIRLINE_CODE||FS2.FLIGHT_NUMBER AS "VUELO2", '\
        'AL2.AIRLINE_NAME "AEROLINEA2", '\
        'A2.AIRPORT_NAME "AEROPUERTO2", '\
        'P2.PLACENAME "LUGAR2", '\
        'PT2.DESPLACETYPE "TIPO_LUGAR2", '\
        'P2_1.PLACENAME "LUGAR_SUP2", '\
        'PT2_1.DESPLACETYPE "TIPO_LUGAR_SUP2", '\
        'P2_2.PLACENAME "LUGAR_SUP_SUP_2", '\
        'PT2_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP2", '\
        'FS2.FLIGHT_SEGMENT_DATE "FECHA2", '\
        'FS2.FLIGHT_SEGMENT_HOUR "HORA2", '\
        'PE2.NAME "PILOTO2" '\
        'FROM FLIGHT_CONNECTION FC '\
        'INNER JOIN FLIGHT_SEGMENT FS1 ON FS1.AIRLINE_CODE = FC.FLI_AIRLINE_CODE AND FS1.FLIGHT_NUMBER = FC.FLI_FLIGHT_NUMBER AND FS1.AIRPORT_CODE = FC.FLI_AIRPORT_CODE '\
        'INNER JOIN FLIGHT FL1 ON FL1.AIRLINE_CODE = FS1.AIRLINE_CODE AND FL1.FLIGHT_NUMBER = FS1.FLIGHT_NUMBER '\
        'INNER JOIN AIRLINE AL1 ON AL1.AIRLINE_CODE = FL1.AIRLINE_CODE '\
        'INNER JOIN AIRPORT A1 ON A1.AIRPORT_CODE = FS1.AIRPORT_CODE '\
        'INNER JOIN PLACE P1 ON P1.IDPLACE = A1.IDPLACE '\
        'INNER JOIN PLACETYPE PT1 ON PT1.IDPLACETYPE = P1.IDPLACETYPE '\
        'INNER JOIN PLACE P1_1 ON P1_1.IDPLACE = P1.PLA_IDPLACE '\
        'INNER JOIN PLACETYPE PT1_1 ON PT1_1.IDPLACETYPE = P1_1.IDPLACETYPE '\
        'INNER JOIN PLACE P1_2 ON P1_2.IDPLACE = P1_1.PLA_IDPLACE '\
        'INNER JOIN PLACETYPE PT1_2 ON PT1_2.IDPLACETYPE = P1_2.IDPLACETYPE '\
        'INNER JOIN PILOT_ASSIGMENT PA1 ON PA1.AIRLINE_CODE = FS1.AIRLINE_CODE AND PA1.FLIGHT_NUMBER = FS1.FLIGHT_NUMBER AND PA1.AIRPORT_CODE = FS1.AIRPORT_CODE '\
        'INNER JOIN PILOT PL1 ON PL1.PILOT_LICENSE = PA1.PILOT_LICENSE '\
        'INNER JOIN EMPLOYEE E1 ON E1.AIRLINE_CODE = PL1.AIRLINE_CODE AND E1.EMPLOYEE_NUMBER = PL1.EMPLOYEE_NUMBER '\
        'INNER JOIN PERSON PE1 ON PE1.IDPERSON = E1.IDPERSON '\
        'INNER JOIN FLIGHT_SEGMENT FS2 ON FS2.AIRLINE_CODE = FC.AIRLINE_CODE AND FS2.FLIGHT_NUMBER = FC.FLIGHT_NUMBER AND FS2.AIRPORT_CODE = FC.AIRPORT_CODE '\
        'INNER JOIN FLIGHT FL2 ON FL2.AIRLINE_CODE = FS2.AIRLINE_CODE AND FL2.FLIGHT_NUMBER = FS2.FLIGHT_NUMBER '\
        'INNER JOIN AIRLINE AL2 ON AL2.AIRLINE_CODE = FL2.AIRLINE_CODE '\
        'INNER JOIN AIRPORT A2 ON A2.AIRPORT_CODE = FS2.AIRPORT_CODE '\
        'INNER JOIN PLACE P2 ON P2.IDPLACE = A2.IDPLACE '\
        'INNER JOIN PLACETYPE PT2 ON PT2.IDPLACETYPE = P2.IDPLACETYPE '\
        'INNER JOIN PLACE P2_1 ON P2_1.IDPLACE = P2.PLA_IDPLACE '\
        'INNER JOIN PLACETYPE PT2_1 ON PT2_1.IDPLACETYPE = P2_1.IDPLACETYPE '\
        'INNER JOIN PLACE P2_2 ON P2_2.IDPLACE = P2_1.PLA_IDPLACE '\
        'INNER JOIN PLACETYPE PT2_2 ON PT2_2.IDPLACETYPE = P2_2.IDPLACETYPE '\
        'INNER JOIN PILOT_ASSIGMENT PA2 ON PA2.AIRLINE_CODE = FS2.AIRLINE_CODE AND PA2.FLIGHT_NUMBER = FS2.FLIGHT_NUMBER AND PA2.AIRPORT_CODE = FS2.AIRPORT_CODE '\
        'INNER JOIN PILOT PL2 ON PL2.PILOT_LICENSE = PA2.PILOT_LICENSE '\
        'INNER JOIN EMPLOYEE E2 ON E2.AIRLINE_CODE = PL2.AIRLINE_CODE AND E2.EMPLOYEE_NUMBER = PL2.EMPLOYEE_NUMBER '\
        'INNER JOIN PERSON PE2 ON PE2.IDPERSON = E2.IDPERSON '\
        'WHERE  FC.FLI_AIRLINE_CODE = :1 AND '\
        'FC.FLI_FLIGHT_NUMBER = :2 AND '\
        'FC.FLI_AIRPORT_CODE = :3 AND '\
        'FC.AIRLINE_CODE = :4 AND '\
        'FC.FLIGHT_NUMBER = :5 AND '\
        'FC.AIRPORT_CODE = :6', busqueda_1)
        datos_conexion = list(datos_conexion)     
        existeSiguienteSeg = True

        datos_segments = []
        while(existeSiguienteSeg):
            busqueda_2 = (aerolinea2, no_vuelo2, aeropuerto2)
            datos_segment_siguiente = conexion.getCursor().execute('SELECT AL.AIRLINE_CODE||F.FLIGHT_NUMBER AS "VUELO", '\
            'AL.AIRLINE_NAME "AEROLINEA", '\
            'AD.AIRPORT_CODE "COD AEROPUERTO DESTINO", '\
            'AD.AIRPORT_NAME "AEROPUERTO DESTINO", '\
            'PD.PLACENAME "LUGAR DESTINO", '\
            'PTD.DESPLACETYPE "TIPO LUGAR DESTINO", '\
            'PD_1.PLACENAME "LUGAR_SUP_DESTINO", '\
            'PTD_1.DESPLACETYPE "TIPO_LUGAR_SUP_DESTINO", '\
            'PD_2.PLACENAME "LUGAR_SUP_SUP_DESTINO", '\
            'PTD_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP_DESTINO", '\
            'FS.FLIGHT_SEGMENT_DATE "FECHA", '\
            'FS.FLIGHT_SEGMENT_HOUR "HORA", '\
            'PE.NAME "PILOTO" '\
            'FROM FLIGHT_SEGMENT FS '\
            'INNER JOIN FLIGHT F ON F.AIRLINE_CODE = FS.AIRLINE_CODE AND F.FLIGHT_NUMBER = FS.FLIGHT_NUMBER '\
            'INNER JOIN AIRLINE AL ON AL.AIRLINE_CODE = F.AIRLINE_CODE '\
            'INNER JOIN AIRPORT AD ON AD.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PLACE PD ON PD.IDPLACE = AD.IDPLACE '\
            'INNER JOIN PLACETYPE PTD ON PTD.IDPLACETYPE = PD.IDPLACETYPE '\
            'INNER JOIN PLACE PD_1 ON PD_1.IDPLACE = PD.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_1 ON PTD_1.IDPLACETYPE = PD_1.IDPLACETYPE '\
            'INNER JOIN PLACE PD_2 ON PD_2.IDPLACE = PD_1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_2 ON PTD_2.IDPLACETYPE = PD_2.IDPLACETYPE '\
            'INNER JOIN PILOT_ASSIGMENT PA ON PA.AIRLINE_CODE = FS.AIRLINE_CODE AND PA.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND PA.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PILOT P ON P.PILOT_LICENSE = PA.PILOT_LICENSE '\
            'INNER JOIN EMPLOYEE E ON E.AIRLINE_CODE = P.AIRLINE_CODE AND E.EMPLOYEE_NUMBER = P.EMPLOYEE_NUMBER '\
            'INNER JOIN PERSON PE ON PE.IDPERSON = E.IDPERSON '\
            'WHERE '\
            'FS.AIRLINE_CODE = :1 AND '\
            'FS.FLIGHT_NUMBER = :2 AND '\
            'FS.AIR_AIRPORT_CODE = :3 ', busqueda_2)
            datos_segment_siguiente = list(datos_segment_siguiente)
            if len(datos_segment_siguiente) > 0:
                datos_segment_siguiente = datos_segment_siguiente[0]
                datos_segments.append(datos_segment_siguiente)
                aeropuerto2 = datos_segment_siguiente[2]
            else:
                existeSiguienteSeg = False
        

        return {"success":True, "datos_conexion" : datos_conexion, "datos_segments" : datos_segments}


    except oracledb.DatabaseError as err:    
        
        return {"success":False, "datos_conexion" : [], "datos_segments": [], "error" : str(err)}



def obtener_itinerario(origen, destino):
    try:        
        consulta_origen = (origen,)
        fs_origen = conexion.getCursor().execute("SELECT FS.AIRLINE_CODE, FS.FLIGHT_NUMBER, FS.AIR_AIRPORT_CODE FROM FLIGHT_SEGMENT FS WHERE FS.AIR_AIRPORT_CODE = :1 ",consulta_origen)
        fs_origen = list(fs_origen)
        
        itinerarios = []        
        for fso in fs_origen:
            verificar_segment(itinerarios,[], fso[0], fso[1], origen, destino)

        return {"success":True, "itinerarios":itinerarios}
    except oracledb.DatabaseError as err:    
        return {"success":False, "itinerarios": [], "error" : str(err)}

def verificar_segment(itinerarios,datos_segments, airline, flight_number, origen, destino, conexion_seg = None):
    existeSiguienteSeg = True
    encontroDestino = False
    cod_aeropuerto_origen = origen
    if conexion_seg is not None:
        conexion_seg = conexion_seg[0]
        datos_segments.append(conexion_seg)

    if len(datos_segments) == 0:
        busqueda_segment_origen = (airline, flight_number, origen)
        datos_segment_origen = conexion.getCursor().execute('SELECT AL.AIRLINE_CODE||F.FLIGHT_NUMBER AS "VUELO", '\
            'AL.AIRLINE_NAME "AEROLINEA", '\
            'AO.AIRPORT_CODE "COD AEROPUERTO ORIGEN", '\
            'AO.AIRPORT_NAME "AEROPUERTO ORIGEN", '\
            'PO.PLACENAME "LUGAR ORIGEN", '\
            'PTO.DESPLACETYPE "TIPO LUGAR ORIGEN", '\
            'PO_1.PLACENAME "LUGAR_SUP_ORIGEN", '\
            'PTO_1.DESPLACETYPE "TIPO_LUGAR_SUP_ORIGEN", '\
            'PO_2.PLACENAME "LUGAR_SUP_SUP_ORIGEN", '\
            'PTO_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP_ORIGEN", '\
            'FS.FLIGHT_SEGMENT_DATE "FECHA", '\
            'FS.FLIGHT_SEGMENT_HOUR "HORA", '\
            'PE.NAME "PILOTO" '\
            'FROM FLIGHT_SEGMENT FS '\
            'INNER JOIN FLIGHT F ON F.AIRLINE_CODE = FS.AIRLINE_CODE AND F.FLIGHT_NUMBER = FS.FLIGHT_NUMBER '\
            'INNER JOIN AIRLINE AL ON AL.AIRLINE_CODE = F.AIRLINE_CODE '\
            'INNER JOIN AIRPORT AO ON AO.AIRPORT_CODE = FS.AIR_AIRPORT_CODE '\
            'INNER JOIN PLACE PO ON PO.IDPLACE = AO.IDPLACE '\
            'INNER JOIN PLACETYPE PTO ON PTO.IDPLACETYPE = PO.IDPLACETYPE '\
            'INNER JOIN PLACE PO_1 ON PO_1.IDPLACE = PO.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTO_1 ON PTO_1.IDPLACETYPE = PO_1.IDPLACETYPE '\
            'INNER JOIN PLACE PO_2 ON PO_2.IDPLACE = PO_1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTO_2 ON PTO_2.IDPLACETYPE = PO_2.IDPLACETYPE '\
            'INNER JOIN PILOT_ASSIGMENT PA ON PA.AIRLINE_CODE = FS.AIRLINE_CODE AND PA.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND PA.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PILOT P ON P.PILOT_LICENSE = PA.PILOT_LICENSE '\
            'INNER JOIN EMPLOYEE E ON E.AIRLINE_CODE = P.AIRLINE_CODE AND E.EMPLOYEE_NUMBER = P.EMPLOYEE_NUMBER '\
            'INNER JOIN PERSON PE ON PE.IDPERSON = E.IDPERSON '\
            'WHERE '\
            'FS.AIRLINE_CODE = :1 AND '\
            'FS.FLIGHT_NUMBER = :2 AND '\
            'FS.AIR_AIRPORT_CODE = :3 ', busqueda_segment_origen)
        datos_segment_origen = list(datos_segment_origen)
        datos_segments.append(datos_segment_origen[0])

    while(existeSiguienteSeg):
        busqueda_2 = (airline, flight_number, cod_aeropuerto_origen)
        
        datos_segment_siguiente = conexion.getCursor().execute('SELECT AL.AIRLINE_CODE||F.FLIGHT_NUMBER AS "VUELO", '\
            'AL.AIRLINE_NAME "AEROLINEA", '\
            'AD.AIRPORT_CODE "COD AEROPUERTO DESTINO", '\
            'AD.AIRPORT_NAME "AEROPUERTO DESTINO", '\
            'PD.PLACENAME "LUGAR DESTINO", '\
            'PTD.DESPLACETYPE "TIPO LUGAR DESTINO", '\
            'PD_1.PLACENAME "LUGAR_SUP_DESTINO", '\
            'PTD_1.DESPLACETYPE "TIPO_LUGAR_SUP_DESTINO", '\
            'PD_2.PLACENAME "LUGAR_SUP_SUP_DESTINO", '\
            'PTD_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP_DESTINO", '\
            'FS.FLIGHT_SEGMENT_DATE "FECHA", '\
            'FS.FLIGHT_SEGMENT_HOUR "HORA", '\
            'PE.NAME "PILOTO" '\
            'FROM FLIGHT_SEGMENT FS '\
            'INNER JOIN FLIGHT F ON F.AIRLINE_CODE = FS.AIRLINE_CODE AND F.FLIGHT_NUMBER = FS.FLIGHT_NUMBER '\
            'INNER JOIN AIRLINE AL ON AL.AIRLINE_CODE = F.AIRLINE_CODE '\
            'INNER JOIN AIRPORT AD ON AD.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PLACE PD ON PD.IDPLACE = AD.IDPLACE '\
            'INNER JOIN PLACETYPE PTD ON PTD.IDPLACETYPE = PD.IDPLACETYPE '\
            'INNER JOIN PLACE PD_1 ON PD_1.IDPLACE = PD.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_1 ON PTD_1.IDPLACETYPE = PD_1.IDPLACETYPE '\
            'INNER JOIN PLACE PD_2 ON PD_2.IDPLACE = PD_1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_2 ON PTD_2.IDPLACETYPE = PD_2.IDPLACETYPE '\
            'INNER JOIN PILOT_ASSIGMENT PA ON PA.AIRLINE_CODE = FS.AIRLINE_CODE AND PA.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND PA.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PILOT P ON P.PILOT_LICENSE = PA.PILOT_LICENSE '\
            'INNER JOIN EMPLOYEE E ON E.AIRLINE_CODE = P.AIRLINE_CODE AND E.EMPLOYEE_NUMBER = P.EMPLOYEE_NUMBER '\
            'INNER JOIN PERSON PE ON PE.IDPERSON = E.IDPERSON '\
            'WHERE '\
            'FS.AIRLINE_CODE = :1 AND '\
            'FS.FLIGHT_NUMBER = :2 AND '\
            'FS.AIR_AIRPORT_CODE = :3 ', busqueda_2)

        datos_segment_siguiente = list(datos_segment_siguiente)
        if len(datos_segment_siguiente) > 0:
            datos_segment_siguiente = datos_segment_siguiente[0]
            datos_segments.append(datos_segment_siguiente)
            cod_aeropuerto_origen = datos_segment_siguiente[2]          
            verificar_conexion(itinerarios, copy.deepcopy(datos_segments), airline, flight_number, cod_aeropuerto_origen, destino)
            if cod_aeropuerto_origen == destino:
                existeSiguienteSeg = False
                encontroDestino = True
        else:
            existeSiguienteSeg = False
            encontroDestino = False
    
    if encontroDestino:
        itinerarios.append(datos_segments)
        return True
    else:
        return False

def verificar_conexion(itinerarios,datos_segments, airline, flight_number, origen, destino):
    #Consultar cuales conexiones tiene ese origen
    consulta_conexion = (airline,flight_number,origen)
    flight_conexion = conexion.getCursor().execute('SELECT FC.AIRLINE_CODE, FC.FLIGHT_NUMBER, FC.AIRPORT_CODE '\
    'FROM FLIGHT_CONNECTION FC WHERE FC.FLI_AIRLINE_CODE = :1 AND FC.FLI_FLIGHT_NUMBER = :2 AND FC.FLI_AIRPORT_CODE = :3 ',consulta_conexion)
    flight_conexion = list(flight_conexion)
    for fc in flight_conexion:
        airline_n = fc[0]
        flight_number_n = fc[1]
        origen_n = fc[2]
        busqueda_conexion_seg = (airline_n, flight_number_n, origen_n)

        datos_segment_conexion = conexion.getCursor().execute('SELECT AL.AIRLINE_CODE||F.FLIGHT_NUMBER AS "VUELO", '\
            'AL.AIRLINE_NAME "AEROLINEA", '\
            'AD.AIRPORT_CODE "COD AEROPUERTO DESTINO", '\
            'AD.AIRPORT_NAME "AEROPUERTO DESTINO", '\
            'PD.PLACENAME "LUGAR DESTINO", '\
            'PTD.DESPLACETYPE "TIPO LUGAR DESTINO", '\
            'PD_1.PLACENAME "LUGAR_SUP_DESTINO", '\
            'PTD_1.DESPLACETYPE "TIPO_LUGAR_SUP_DESTINO", '\
            'PD_2.PLACENAME "LUGAR_SUP_SUP_DESTINO", '\
            'PTD_2.DESPLACETYPE "TIPO_LUGAR_SUP_SUP_DESTINO", '\
            'FS.FLIGHT_SEGMENT_DATE "FECHA", '\
            'FS.FLIGHT_SEGMENT_HOUR "HORA", '\
            'PE.NAME "PILOTO" '\
            'FROM FLIGHT_SEGMENT FS '\
            'INNER JOIN FLIGHT F ON F.AIRLINE_CODE = FS.AIRLINE_CODE AND F.FLIGHT_NUMBER = FS.FLIGHT_NUMBER '\
            'INNER JOIN AIRLINE AL ON AL.AIRLINE_CODE = F.AIRLINE_CODE '\
            'INNER JOIN AIRPORT AD ON AD.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PLACE PD ON PD.IDPLACE = AD.IDPLACE '\
            'INNER JOIN PLACETYPE PTD ON PTD.IDPLACETYPE = PD.IDPLACETYPE '\
            'INNER JOIN PLACE PD_1 ON PD_1.IDPLACE = PD.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_1 ON PTD_1.IDPLACETYPE = PD_1.IDPLACETYPE '\
            'INNER JOIN PLACE PD_2 ON PD_2.IDPLACE = PD_1.PLA_IDPLACE '\
            'INNER JOIN PLACETYPE PTD_2 ON PTD_2.IDPLACETYPE = PD_2.IDPLACETYPE '\
            'INNER JOIN PILOT_ASSIGMENT PA ON PA.AIRLINE_CODE = FS.AIRLINE_CODE AND PA.FLIGHT_NUMBER = FS.FLIGHT_NUMBER AND PA.AIRPORT_CODE = FS.AIRPORT_CODE '\
            'INNER JOIN PILOT P ON P.PILOT_LICENSE = PA.PILOT_LICENSE '\
            'INNER JOIN EMPLOYEE E ON E.AIRLINE_CODE = P.AIRLINE_CODE AND E.EMPLOYEE_NUMBER = P.EMPLOYEE_NUMBER '\
            'INNER JOIN PERSON PE ON PE.IDPERSON = E.IDPERSON '\
            'WHERE '\
            'FS.AIRLINE_CODE = :1 AND '\
            'FS.FLIGHT_NUMBER = :2 AND '\
            'FS.AIRPORT_CODE = :3 ', busqueda_conexion_seg)
        datos_segment_conexion = list(datos_segment_conexion)
        

        verificar_segment(itinerarios,copy.deepcopy(datos_segments), airline_n, flight_number_n, origen_n, destino, datos_segment_conexion)
