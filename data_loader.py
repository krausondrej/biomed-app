# data_loader.py
import os
import pandas as pd
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

excel_path = os.path.join(base_path, "ExportedData.xlsx")
style_path = os.path.join(base_path, "resources", "style.qss")

df_all = pd.read_excel(excel_path)

if 'Date of Operation' in df_all.columns:
    df_all['Date of Operation'] = pd.to_datetime(
        df_all['Date of Operation'], errors='coerce')
    df_all['Year'] = df_all['Date of Operation'].dt.year
else:
    df_all['Year'] = None


def load_preop_data():
    """
    Načte a přejmenuje sloupce pro Preoperative stránku,
    převede potřebné sloupce na numerické hodnoty a spočítá agregáty.
    """
    df = df_all.copy()
    df = df.rename(columns={
        'Gender of the patient': 'Gender',
        'Age of patient at day of operation': 'Age',
        'BMI': 'BMI',
        'Please specify the patient\'s comorbidities::No Comorbidities': 'No_Comorbidities',
        'Please specify the patient\'s comorbidities::Diabetes mellitus': 'Diabetes',
        'Please specify the patient\'s comorbidities::COPD': 'COPD',
        'Please specify the patient\'s comorbidities::Hepatic disease': 'Hepatic_Disease',
        'Please specify the patient\'s comorbidities::Renal disease': 'Renal_Disease',
        'Please specify the patient\'s comorbidities::Abdominal aortic aneurysm': 'Aortic_Aneurysm',
        'Please specify the patient\'s comorbidities::Smoker': 'Smoker',
        'Pain at the site of the hernia\nIn rest (laying down)': 'Pain_rest',
        'Pain at the site of the hernia\nDuring activities (walking, biking, sports)': 'Pain_activity',
        'Pain at the site of the hernia\nPain felt during the last week': 'Pain_last_week',
        'Restrictions of activities\nDaily activities (inside the house)': 'Restrict_inside',
        'Restrictions of activities\nOutside the house (walking, biking; driving)': 'Restrict_outside',
        'Restrictions of activities\nDuring sports': 'Restrict_sports',
        'Restrictions of activities\nDuring heavy labour': 'Restrict_heavy',
        'Esthetical discomfort\nThe shape of your abdomen': 'Esthetic_abdomen',
        'Esthetical discomfort\nThe hernia itself': 'Esthetic_hernia',
    })
    df['BMI'] = pd.to_numeric(df['BMI'], errors='coerce')

    restrict_cols = ['Restrict_inside', 'Restrict_outside',
                     'Restrict_sports', 'Restrict_heavy']
    df[restrict_cols] = (
        df[restrict_cols]
        .apply(pd.to_numeric, errors='coerce')
        .fillna(0)
        .astype(int)
    )
    pain_cols = ['Pain_rest', 'Pain_activity', 'Pain_last_week']
    df[pain_cols] = (
        df[pain_cols]
        .apply(pd.to_numeric, errors='coerce')
        .fillna(0)
        .astype(int)
    )
    aesth_cols = ['Esthetic_abdomen', 'Esthetic_hernia']
    df[aesth_cols] = (
        df[aesth_cols]
        .apply(pd.to_numeric, errors='coerce')
        .fillna(0)
        .astype(int)
    )

    df['Preop_Restrict_Score'] = df[restrict_cols].sum(axis=1)
    df['Preop_Pain_Score'] = df[pain_cols].sum(axis=1)
    df['Esthetic_Discomfort_Score'] = df[aesth_cols].sum(axis=1)

    for col in ['No_Comorbidities', 'Diabetes', 'COPD', 'Hepatic_Disease', 'Renal_Disease', 'Aortic_Aneurysm', 'Smoker']:
        df[col] = df[col].fillna(0).astype(int)

    return df


def load_oper_data():
    df = df_all.copy()
    df = df.rename(columns={
        'Gender of the patient': 'Gender',
        'Age of patient at day of operation': 'Age',
        'Please choose the indication for the abdominal wall repair': 'Operation_Type',
        'Indication for the surgery?': 'Indication',
        'Side of the groin hernia? Bilateral?::Right': 'GHR_Side_Right',
        'Side of the groin hernia? Bilateral?::Left': 'GHR_Side_Left',
        'Number of previous repairs - right side': 'GHR_Prev_Repairs_Right',
        'Number of previous repairs - left side': 'GHR_Prev_Repairs_Left',
        'Type of the groin hernia - right side::Lateral (indirect)': 'GHR_Type_Right_Lateral',
        'Type of the groin hernia - right side::Medial (direct)': 'GHR_Type_Right_Medial',
        'Type of the groin hernia - right side::Femoral': 'GHR_Type_Right_Femoral',
        'Type of the groin hernia - right side::Obturator': 'GHR_Type_Right_Obturator',
        'Type of the groin hernia - left side::Lateral (indirect)': 'GHR_Type_Left_Lateral',
        'Type of the groin hernia - left side::Medial (direct)': 'GHR_Type_Left_Medial',
        'Type of the groin hernia - left side::Femoral': 'GHR_Type_Left_Femoral',
        'Type of the groin hernia - left side::Obturator': 'GHR_Type_Left_Obturator',
        'Type of stoma': 'PHR_Stoma_Type',
        'Number of previous parastomal hernia repairs': 'PHR_Prev_Repairs',
        'Please specify type of primary ventral hernia': 'PVHR_Subtype',
        'Number of previous hernia repairs': 'IVHR_Prev_Repairs',
    })

    op_map = {
        'Groin Hernia Repair':        'GHR',
        'Parastomal Hernia Repair':    'PHR',
        'Primary Ventral Hernia Repair': 'PVHR',
        'Incisional Ventral Hernia Repair': 'IVHR'
    }
    df['Operation_Type'] = df['Operation_Type'].map(op_map)
    return df


def load_discharge_data():
    df = df_all.copy()
    df = df.rename(columns={
        'Gender of the patient': 'Gender',
        'Age of patient at day of operation': 'Age',
        'Please choose the indication for the abdominal wall repair': 'Operation_Type',
        'Where there intrahospital  complications ?': 'Intra_Complications',
        'Please enter the type of intrahospital complications::Bleeding complications': 'Comp_Bleeding',
        'Please enter the type of intrahospital complications::Surgical site infection (SSI)': 'Comp_SSI',
        'Please enter the type of intrahospital complications::Mesh infection': 'Comp_Mesh_Infection',
        'Please enter the type of intrahospital complications::Hematoma': 'Comp_Hematoma',
        'Please enter the type of intrahospital complications::Prolonged ileus or obstruction': 'Comp_Prolonged_Ileus',
        'Please enter the type of intrahospital complications::Urinary retention': 'Comp_Urinary_Retention',
        'Please enter the type of intrahospital complications::General complications': 'Comp_General',
    })
    for col in ['Comp_Bleeding', 'Comp_SSI', 'Comp_Mesh_Infection', 'Comp_Hematoma', 'Comp_Prolonged_Ileus', 'Comp_Urinary_Retention', 'Comp_General']:
        df[col] = df[col].fillna(0).astype(int)

    op_map = {
        'Groin Hernia Repair':        'GHR',
        'Parastomal Hernia Repair':    'PHR',
        'Primary Ventral Hernia Repair': 'PVHR',
        'Incisional Ventral Hernia Repair': 'IVHR'
    }
    df['Operation_Type'] = df_all['Please choose the indication for the abdominal wall repair']\
        .map(op_map)
    return df


def load_followup_data():
    df = df_all.copy()
    df = df.rename(columns={
        'Gender of the patient': 'Gender',
        'Age of patient at day of operation': 'Age',
        'Where there  complications at Follow Up ?': 'Followup_Complications',
        'Please enter the type of complications at Follow Up::Seroma': 'FU_Seroma',
        'Please enter the type of complications at Follow Up::Hematoma': 'FU_Hematoma',
        'Please enter the type of complications at Follow Up::Pain': 'FU_Pain',
        'Please enter the type of complications at Follow Up::Surgical site infection (SSI)': 'FU_SSI',
        'Please enter the type of complications at Follow Up::Mesh infection': 'FU_Mesh_Infection',
        'Please enter the type of complications at Follow Up::Other': 'FU_Other',
    })
    for col in ['FU_Seroma', 'FU_Hematoma', 'FU_Pain', 'FU_SSI', 'FU_Mesh_Infection', 'FU_Other']:
        df[col] = df[col].fillna(0).astype(int)
    return df
