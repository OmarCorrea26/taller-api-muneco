# apendice_r/etapa_plumber.R
# La misma etapa, en R con {plumber}. El contrato es JSON, asi que al ensamblador no le
# importa el lenguaje: si respondes en el puerto correcto con la forma correcta, tu parte
# del muneco sale derecha. Ejemplo con la etapa 3 (calibrar).
#
#   install.packages(c("plumber", "jsonlite", "dplyr"))
#   Rscript -e "plumber::pr_run(plumber::pr('apendice_r/etapa_plumber.R'), port = 8003)"

library(plumber)
library(jsonlite)
library(dplyr)

NUMERO <- 3
objetivo <- fromJSON("contrato/poblacion_objetivo.json")

#* Estado del servicio
#* @get /salud
function() {
  list(etapa = NUMERO, nombre = "calibrar", estado = "ok")
}

#* Procesa la entrada de la etapa
#* @post /procesar
#* @serializer unboxedJSON
function(req) {
  entrada <- fromJSON(req$postBody)
  df <- as_tibble(entrada$registros)

  suma_cruda <- df %>% group_by(departamento) %>% summarise(s = sum(factor_expansion))
  razon <- setNames(unlist(objetivo[suma_cruda$departamento]) / suma_cruda$s, suma_cruda$departamento)
  df <- df %>% mutate(factor_calibrado = factor_expansion * razon[departamento])

  totales <- df %>% group_by(departamento) %>% summarise(t = sum(factor_calibrado))
  list(
    registros = df,
    resumen = list(
      totales_por_departamento = as.list(setNames(totales$t, totales$departamento)),
      poblacion_objetivo = lapply(objetivo, as.numeric)
    )
  )
}
