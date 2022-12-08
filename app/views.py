from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.api.view_api import obtener_aerolineas, obtener_aeropuertos, crear_vuelo, datos_vuelo, crear_conexion, datos_conexion, obtener_itinerario
public_bp = Blueprint("public", __name__, url_prefix="/")

@public_bp.route('/vuelo/nuevo')
def nuevo_vuelo():
    aerolineas = obtener_aerolineas()
    aeropuertos = obtener_aeropuertos()
    
    info = {"aerolineas": aerolineas["aerolineas"], "aeropuertos": aeropuertos["aeropuertos"]}

    return render_template('nuevo_vuelo.html', info=info)
    

@public_bp.route('/vuelo/nuevo',methods=['POST'])
def agregar_vuelo():
    res = crear_vuelo(request)
    if res["success"]:
        return redirect(url_for('public.mostrar_vuelo',aerolinea=request.form.get('aerolinea'), no_vuelo=request.form.get('no_vuelo')))
    else:
        return res["error"]


@public_bp.route('/vuelo/mostrar/<aerolinea>/<no_vuelo>')
def mostrar_vuelo(aerolinea, no_vuelo):
    datos = datos_vuelo(aerolinea, no_vuelo)
    datos = datos["datos_vuelo"]
    data_final = []
    for (i,dato) in enumerate(datos):
        item = {"vuelo": dato[0], "aerolinea": dato[1], "aeropuerto": dato[2], "fecha": dato[7], "hora": dato[8],"piloto": dato[4]}
        item["place"] = []
        item["place"].append((dato[9][1],dato[9][0]))
        item["place"].append((dato[9][3],dato[9][2]))
        item["place"].append((dato[9][5],dato[9][4]))

        data_final.append(item)
        #ultima_fila
        if (i+1) == len(datos):
            itemf = {"vuelo": dato[0], "aerolinea": dato[1], "aeropuerto": dato[3], "fecha": "", "hora": "","piloto": ""}
            itemf["place"] = []
            itemf["place"].append((dato[10][1],dato[10][0]))
            itemf["place"].append((dato[10][3],dato[10][2]))
            itemf["place"].append((dato[10][5],dato[10][4]))

            data_final.append(itemf)


    info = {"aerolinea": aerolinea, "no_vuelo": no_vuelo, "data": data_final}

    return render_template('datos_vuelo.html', info=info)


@public_bp.route('/vuelo/conexion')
def nueva_conexion():
    aerolineas = obtener_aerolineas()
    
    info = {"aerolineas": aerolineas["aerolineas"]}

    return render_template('nueva_conexion.html', info=info)

@public_bp.route('/vuelo/conexion',methods=['POST'])
def agregar_conexion():
    if(request.form.get("aeropuerto1") != request.form.get("aeropuerto2")):
        flash("Los aeropuertos deben ser iguales", 'danger')
        return redirect(url_for('public.agregar_conexion'))

    res = crear_conexion(request)
    if res["success"]:        
        return redirect(url_for('public.mostrar_conexion',aerolinea1 = request.form.get("aerolinea1"), no_vuelo1 = request.form.get("vuelo1"), aeropuerto1 = request.form.get("aeropuerto1"), aerolinea2 = request.form.get("aerolinea2"), no_vuelo2 = request.form.get("vuelo2"), aeropuerto2 = request.form.get("aeropuerto2")))
    else:
        flash(res["error"], 'danger')
        return redirect(url_for('public.agregar_conexion'))

@public_bp.route('/vuelo/conexion/<aerolinea1>/<no_vuelo1>/<aeropuerto1>/<aerolinea2>/<no_vuelo2>/<aeropuerto2>')
def mostrar_conexion(aerolinea1, no_vuelo1,aeropuerto1,aerolinea2,no_vuelo2,aeropuerto2):
    datos = datos_conexion(aerolinea1, no_vuelo1,aeropuerto1,aerolinea2,no_vuelo2,aeropuerto2)

    return render_template('datos_conexion.html', info=datos)

@public_bp.route('/itinerario')
def iterinario():
    aeropuertos = obtener_aeropuertos()

    info = {"aeropuertos": aeropuertos["aeropuertos"]}

    return render_template('iterinario.html', info=info)

@public_bp.route('/itinerario',methods=['POST'])
def consultar_iterinario():
    itinerario = obtener_itinerario(request.form.get('aeropuerto_origen'), request.form.get('aeropuerto_destino'))
    itinerario_organizado = []

    j = 1
    for itinerario_it in itinerario["itinerarios"]:
        item_itinerario_organizado = {"num_itinerario":j, "itinerario":[]}
        for i in range(len(itinerario_it) - 1):
            item_it_actual = itinerario_it[i]
            item_it_proximo = itinerario_it[i+1]
            if item_it_actual[0] == item_it_proximo[0]:
                item_itinerario = {"tipo": "Trayecto", "item_1": item_it_actual, "item_2": item_it_proximo}
            else:
                item_itinerario = {"tipo": "Conexion", "item_1": item_it_actual, "item_2": item_it_proximo}

            item_itinerario_organizado["itinerario"].append(item_itinerario)

        itinerario_organizado.append(item_itinerario_organizado)
        j+=1

    info = {"itinerario_organizado": itinerario_organizado, "origen": request.form.get('aeropuerto_origen'), "destino": request.form.get('aeropuerto_destino')}

    return render_template('ver_itinerario.html', info=info)