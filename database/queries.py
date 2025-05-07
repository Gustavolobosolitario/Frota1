from database.db_connection import fetch_data

def get_empreendimentos():
    query = """SELECT DISTINCT idEmpCV, idEmpSienge, descEmpreendimento FROM com_cv_dim_empreendimentos ORDER BY descEmpreendimento ASC"""
    return fetch_data(query)

def get_modulo():
    query = f"""
                SELECT 
                DISTINCT 
                    idEmpCv ,
                    modulo 
                FROM com_view_fct_mapaDisponibilidade md
                WHERE 
                    1=1
                ORDER BY idEmpCv , modulo ASC
            """
    return fetch_data(query=query)

def get_bloco():
    query = f"""
                SELECT 
                    DISTINCT 
                        idEmpCv ,
                        modulo ,
                        bloco 
                FROM com_view_fct_mapaDisponibilidade md
                ORDER BY idEmpCv , modulo, bloco ASC

             """
    return fetch_data(query=query)