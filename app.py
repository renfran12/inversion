from flask import render_template
import flask
from flask import send_from_directory, request
import pandas as pd
import json
import plotly
import plotly.express as px


data = pd.read_csv('FDI_Case_Study.csv', header=0)
datai = data.set_index('Sector', drop=True)
app = flask.Flask(__name__)


def buscar_fid(sector, año):
    valor = datai.at[sector, año]
    return valor


def maxmin(parametro, fecha):
    valorm = 0
    if parametro == 'maximo':
        datamax = datai[fecha]
        valorm = datamax.idxmax()
    elif parametro == 'minimo':
        datamin = datai[fecha]
        valorm = datamin.idxmin()
    return valorm


def crecimiento(top, fechai, fechaf, decre):
    datac = datai.diff(axis = 'columns')
    datac = datac.loc[:, fechai:fechaf]
    datac['Variación_FID'] = datac.sum(axis = 'columns')
    if decre == 'decrecimiento':
        datac = datac.sort_values(by=['Variación_FID'], ascending=True).head(top)
    elif decre == 'crecimiento':
        datac = datac.sort_values(by=['Variación_FID'], ascending=False).head(top)
    index = datac.index
    return index


def proporcion():
    datap = datai
    datap['FID SUM'] = datap.sum(axis='columns', numeric_only=True)
    porcentaje = datap["FID SUM"].max()/datap["FID SUM"].sum()*100
    sector = datap["FID SUM"].idxmax()
    resp = (porcentaje, sector)
    return resp


@app.route('/')
def notdash():
   df = pd.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
   })
   fig = px.bar(df, x='Fruit', y='Amount', color='City',    barmode='group')
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('notdash.html', graphJSON=graphJSON)

@app.route('/home')
def home():
    return "Hello World"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True,force=True)
    fulfillmentText = ''
    query_result = req.get('queryResult')
    if query_result.get('action') == 'fidporsector':
        try:
            sector = str(query_result.get('parameters').get('sector'))
            fecha1 = str(query_result.get('parameters').get('fecha'))
            valor = buscar_fid(sector, fecha1)
            fulfillmentText = f'El sector: {sector} tiene un FID de: {valor} en {fecha1}'
        except:
            fulfillmentText = 'Intente nuevamente'

    elif query_result.get('action') == 'maxmin':
        try:
            param = str(query_result.get('parameters').get('maxminfiltro'))
            fecha2 = str(query_result.get('parameters').get('maxminfecha'))
            sectorm = maxmin(param, fecha2)
            if param == 'maximo':
                fulfillmentText = f'El sector: {sectorm} tiene el FID máximo del año {fecha2}'
            elif param == 'minimo':
                fulfillmentText = f'El sector: {sectorm} tiene el FID mínimo del año {fecha2}'
        except:
            fulfillmentText = 'Intente de nuevo'

    elif query_result.get('action') == 'crecimiento':
        try:
            crede = str(query_result.get('parameters').get('crede'))
            fechai = str(query_result.get('parameters').get('fechai'))
            fechaf = str(query_result.get('parameters').get('fechaf'))
            cant = int(query_result.get('parameters').get('cant'))
            resp = crecimiento(cant,fechai,fechaf, crede)
            fulfillmentText = f'Hola {resp}'
        except:
            fulfillmentText = 'Intente de nuevo'

    elif query_result.get('action') == 'proporcion':
        try:
            tupla = proporcion()
            fulfillmentText = f'El sector {tupla[1]} tiene la mayor proporción con el {round(tupla[0],2)}% de participación de inversión'
        except:
            fulfillmentText = 'Intente de nuevo'

    return {
        'fulfillmentText': fulfillmentText
    }


if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
