'''
Created on Dec 9, 2016

@author: XBBKKL3
'''
import pandas as pd
import statsmodels.api as sm
import re; #regular expression
import numpy as np
import os


WORKING_PATH = "C:/workspace2016Python"
cwd = os.chdir(WORKING_PATH)

OUTPUT_PATH = WORKING_PATH+"/Revenue_Output_12152016"
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

#####Class Definition
class MacroFactor:
    def __init__(self, factordata, historyenddate):
        self.factorData = factordata
        self.factorName = factordata.columns.values
        self.historyStartDate = factordata.index[0]
        self.historyEndDate = historyenddate
        self.forecastStartDate = factordata.index[factordata.index>self.historyEndDate][0]
        self.forecastEndDate = factordata.index[-1]
        
    def displayMacroFactor(self):
        print "-----Factor-----"
        print self.factorName
        print "-----Factor Data-----"
        print self.factorData.head(2)
        print "-----History Start Date-----"
        print self.historyStartDate
        print "-----History End Date-----"
        print self.historyEndDate
        print "-----Forecast Start Date-----"
        print self.forecastStartDate
        print "-----Forecast End Date-----"
        print self.forecastEndDate
        
    def compareMacroFactor(self, compareMacro):
        print "History Start Date: ", self.historyStartDate==compareMacro.historyStartDate
        print "History End Date: ", self.historyEndDate==compareMacro.historyEndDate
        print "Forecast Start Date: ", self.forecastStartDate==compareMacro.forecastStartDate
        print "Forecast End Date: ", self.forecastEndDate==compareMacro.forecastEndDate
        print "All Dates: ", all(self.factorData.index == compareMacro.factorData.index)
        print "All Variables: ", all(self.factorData.columns.values == compareMacro.factorData.columns.values)
        #compare each variables
        mutualVariables = set(self.factorData.columns)&set(compareMacro.factorData.columns)
        print "-----Test Variables: History Not Match----"
        variables_not_match = []
        for variable in mutualVariables:
            data1_history = self.factorData[variable][self.factorData.index < HISTORY_END_DATE].dropna()
            data2_history = compareMacro.factorData[variable][compareMacro.factorData.index < HISTORY_END_DATE].dropna()
            if all(data1_history == data2_history)==False:
                variables_not_match.append(variable)
        print variables_not_match
        return variables_not_match
    
    def selectMacroFactor(self, selectedvariabels):
        if all(variable in self.factorName for variable in selectedvariabels) == False:
            print "Variable Name is not in the Macro File", selectedvariabels;
            return -1;
        else:
            return MacroFactor(self.factorData[selectedvariabels], HISTORY_END_DATE)

class BusinessData:
    def __init__(self, revenueandmetric, revenuename, parentname, metric_or_revenue_as_regresor=None):
        #assign original data
        self.revenueAndMetric = revenueandmetric
        #assign hierarchy
        self.revenueName = revenuename
        self.parentName = parentname
        #assign model on what
        if metric_or_revenue_as_regresor is None:
            self.whatToModel = REVENUE
        else:
            self.whatToModel = metric_or_revenue_as_regresor
        #get revenue, metric attributes
        for i in revenueandmetric.columns:
            if len(re.findall('Revenue',i)):
                revenue_column = i
            if len(re.findall('Metric',i)):
                metric_column = i       
        self.revenueData = revenueandmetric[revenue_column].dropna()
        self.metricData = revenueandmetric[metric_column].dropna()
        if (len(self.revenueData) > 0):
            self.revenueStartDate = self.revenueData.index[0]
            self.revenueEndDate = self.revenueData.index[-1]
        else:
            self.revenueStartDate = None
            self.revenueEndDate = None
        if (len(self.metricData) > 0):
            self.metricStartDate = self.metricData.index[0]
            self.metricEndDate = self.metricData.index[-1]
        else:
            self.metricStartDate = None
            self.metricEndDate = None
        #calculate implied yield
        self.calculateImpliedYield();
        
    def calculateImpliedYield(self):
        impliedyld = self.revenueData/self.metricData
        self.impliedYield = impliedyld[np.isfinite(impliedyld)]
    
    def getModelStartDate(self):
        if self.whatToModel == METRIC:
            return self.metricStartDate
        else:
            return self.revenueStartDate
        
    def getModelEndDate(self):
        if self.whatToModel == METRIC:
            return self.metricEndDate
        else:
            return self.revenueEndDate
    
    def getModelData(self):
        if self.whatToModel == METRIC:
            return self.metricData
        else:
            return self.revenueData
    
    def displayBusinessData(self):
        print "-----RevenueName: " + self.revenueName + ". Parent Name: " + self.parentName
        print "-----Revenue or Metric?-----"
        print self.whatToModel
        print "-----Revenue and Metric-----"
        print self.revenueAndMetric.head(2)
        print "-----Revenue-----"
        print self.revenueData.head(2)
        print "-----Revenue Start Date-----"
        print self.revenueStartDate
        print "-----Revenue End Date-----"
        print self.revenueEndDate
        
        print "-----Metric-----"
        print self.metricData.head(2)
        print "-----Metric Start Date-----"
        print self.metricStartDate
        print "-----Metric End Date-----"
        print self.metricEndDate
        
        print "-----Implied Yield-----"
        print self.impliedYield.head(2)

class StatModel:
    def __init__(self, approach, bu_data, macro_data):

        if bu_data.__class__.__name__ == "BusinessData":
            self.buData = bu_data
        else:
            print "Type of business data is not BusinessData", bu_data.__class__.__name__

        if macro_data.__class__.__name__ == "MacroFactor":
            self.macroData = macro_data
        else:
            print "Type of macro data is not MacroFactor", macro_data.__class__.__name__

        self.modelingapproach = approach
        
    def changeMacroFactors(self, alternative_macro_factor):
        if alternative_macro_factor.__class__.__name__ == "MacroFactor":
            self.macroData = alternative_macro_factor
        else:
            print "Type of macro data is not MacroFactor", alternative_macro_factor.__class__.__name__
        
    def displayStatModel(self):
        print "-----Model-----"
        print self.modelingapproach
        print "-----BU Data-----"
        print self.buData.displayBusinessData()
        print "-----Macro Data-----"
        print self.macroData.displayMacroFactor()
        
class LinearRegression(StatModel):
    def __init__(self, bu_data, macro_data, customizedstartdate = None, customizedenddate = None):
        StatModel.__init__(self, "Linear Regression", bu_data, macro_data)
        if customizedstartdate is not None:
            if customizedstartdate < bu_data.getModelStartDate():
                print "Customized start date is earlier than bu data start date. Abort and use bu data start date."
                self.startDate= bu_data.getModelStartDate()
            else:
                self.startDate = customizedstartdate
        else:
            self.startDate= bu_data.getModelStartDate()
        
        if customizedenddate is not None:
            if customizedenddate > bu_data.getModelEndDate():
                print "Customized end date is later than bu data end date. Abort and use bu data end date"
                self.endDate = bu_data.getModelEndDate
            else:
                self.endDate = customizedenddate
        else:
            self.endDate = bu_data.getModelEndDate()
        self.buData = bu_data
        self.macroData = macro_data
        
    def displayLinearRegression(self):
        StatModel.displayStatModel(self)
        print "-----Model - Start Date:", self.startDate, "; End Date:", self.endDate
        print "-----BU Data----"
        print self.buData.getModelData().head(2)
        print "-----Factor Data----"
        print self.macroData.factorData.head(2)
        
    def getRegressionData(self):
        data = self.buData.getModelData()
        data = pd.concat([data,self.macroData.factorData],axis=1)
        data = data[(data.index <= self.endDate) & (data.index >= self.startDate)]
        return data
    
    def fitLinearRegressionModel(self):
        data = self.getRegressionData().dropna()

        y = data[data.columns[0]]
        x = data[data.columns[1:]]
        x = sm.add_constant(x)
        mod = sm.OLS(y,x)
        res = mod.fit()
        return res
    
    def fitLinearDiffRegressionModel(self):
        data = self.getRegressionData().dropna().diff(periods=1).dropna()

        y = data[data.columns[0]]
        x = data[data.columns[1:]]
        x = sm.add_constant(x)
        mod = sm.OLS(y,x)
        res = mod.fit()
        return res

class Execute_BU_Production:
#     Input are BusinessData, MacroFactor, excel controling file
    def __init__(self, execution_bu_excel, bu, data_bu, macro_data, output_directory):
        self.executionBuExcel = execution_bu_excel
        self.businessUnitName = bu
        self.dataBu = data_bu
        self.macroData = macro_data
        self.outputDirectory = output_directory
        
    def executeBUProduction(self):
        for revenue_name in self.executionBuExcel.columns.values: 
            Execution_Items = self.executionBuExcel[revenue_name]
            Execution_Items = Execution_Items.dropna(axis=0)
            ####BU/Revenue
            what_to_model = revenue_name.split(".")[0]
            revenue_name = revenue_name.split(".")[1]
            
            regressor_name = ['Revenue.'+revenue_name,'Metric.'+revenue_name]
            bu_data = BusinessData(self.dataBu[regressor_name],revenue_name,self.businessUnitName,what_to_model)
            for model_item in range(len(Execution_Items)):
                model = str(Execution_Items.iloc[model_item])
                model = model.replace(" ", "")
                model = model.split(",")
                if (model[0] == "Movingaverage"):
                    pass
                elif (model[0] == "ARIMAX"):
                    pass
                elif (model[0] == "SeasonalDecomposition"):
                    pass
                elif (model[0] == "DiffRegression"):
                    variable_name = model[1:]
                    macroData = self.macroData.selectMacroFactor(variable_name)
                    model_execution = LinearRegression(bu_data,macroData)
                    result = model_execution.fitLinearDiffRegressionModel().summary().__str__()
                    file_name = self.outputDirectory+"/forecast"+self.businessUnitName+"-"+str(Execution_Items.index[model_item])+"-"+what_to_model+"-"+revenue_name+"-fit.txt"
                    f = open(file_name, 'w')
                    f.write(result)
                    f.close()
                else:
                    variable_name = model
                    macroData = self.macroData.selectMacroFactor(variable_name)
                    model_execution = LinearRegression(bu_data,macroData)
                    result = model_execution.fitLinearRegressionModel().summary().__str__()
                    file_name = self.outputDirectory+"/forecast"+self.businessUnitName+"-"+str(Execution_Items.index[model_item])+"-"+what_to_model+"-"+revenue_name+"-fit.txt"
                    f = open(file_name, 'w')
                    f.write(result)
                    f.close()

#####Global Parameters#####
HISTORY_END_DATE = pd.Timestamp('2016-06-30')
METRIC = "Metric"
REVENUE = "Revenue"
ALLSEGMENTS = [1,2,3]

#Input Files
File_Revenue = WORKING_PATH+"/Revenue/Data/RevenuebyLOBv0.3.xlsx";
File_Macro = WORKING_PATH+"/Revenue/Data/Masterfile-Data Process-11-17-16.xlsx";
File_Variable_Selection = WORKING_PATH+"/Revenue/Data/VariableSelection-Revenue-CCAR.xlsx"

#Read Files
scenariobaseline = "Quarterly-baseline";
scenarioadve = "Quarterly-adverse";
scenariosev = "Quarterly-severelyadverse";
scenariobhc = "Quarterly-BHC";
Macro_Q_Baseline = pd.ExcelFile(File_Macro).parse(scenariobaseline, index_col=0)
# Macro_Q_Adv = pd.ExcelFile(File_Macro).parse(scenarioadve, index_col=0)
# Macro_Q_Sev = pd.ExcelFile(File_Macro).parse(scenariosev, index_col=0)
# Macro_Q_Bhc = pd.ExcelFile(File_Macro).parse(scenariobhc, index_col=0)
MACRO_Q_BASELINE = MacroFactor(Macro_Q_Baseline, HISTORY_END_DATE)
# MACRO_Q_ADV = MacroFactor(Macro_Q_Adv, HISTORY_END_DATE)
# MACRO_Q_SEV = MacroFactor(Macro_Q_Sev, HISTORY_END_DATE)
# MACRO_Q_BHC = MacroFactor(Macro_Q_Bhc, HISTORY_END_DATE)

######BU#####
#BU Parameters
BUs = ["CT", "AS","Clearing","CashMgmt", "IM", "BDS", "FX", "SL", "DR","WM"];

Execution_BU = pd.ExcelFile(File_Variable_Selection)
Data_BU = pd.ExcelFile(File_Revenue)
for bu in BUs:
    print bu
    
    OUTPUT_PATH_BU = OUTPUT_PATH+"/"+bu
    if not os.path.exists(OUTPUT_PATH_BU):
        os.makedirs(OUTPUT_PATH_BU)
    
    for segment in ALLSEGMENTS:
        sheetname = bu+str(segment)
        if sheetname not in Execution_BU.sheet_names:
            continue
        if sheetname not in Data_BU.sheet_names:
            continue
         
        Data_Bu_Excel = Data_BU.parse(sheetname, index_col=0)
        OUTPUT_PATH_BU_Result = OUTPUT_PATH_BU+"/"+"Regression-Summary-Segment-"+str(segment)
        if not os.path.exists(OUTPUT_PATH_BU_Result):
            os.makedirs(OUTPUT_PATH_BU_Result)
        
        Execution_BU_Excel = Execution_BU.parse(sheetname, index_col=0)
        Execution_BU_Excel = Execution_BU_Excel.dropna(axis=1,how="all").dropna(axis=0,how="all")
        
        Execute_BU_Production(Execution_BU_Excel, bu, Data_Bu_Excel, MACRO_Q_BASELINE, OUTPUT_PATH_BU_Result).executeBUProduction()
        