from universe_selection import FactorUniverseSelectionModel
from alpha_model import ValueAlphaModel
from portfolio_construction import OptimisationPortfolioConstructionModel
from execution import Execution
from charting import InitCharts, PlotPerformanceChart, PlotPosConcentrationChart, PlotStockCountChart, PlotExposureChart

class TradingBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020,1,1)
        self.SetEndDate(datetime.now() - timedelta(10))
        self.SetCash(100000)
        
        # *Data Resolution
        self.UniverseSettings.Resolution = Resolution.Minute
        
        # *Universe selection model; runs with the above data resolution 
        # custom universe selection model class created -- from universe_selection -->UniverseSelectionModel()
        self.securities = []
        self.CustomUniverseSelectionModel = FactorUniverseSelectionModel(self)
        self.AddUniverse(self.CustomUniverseSelectionModel.SelectCoarse, self.CustomUniverseSelectionModel.SelectFine)
        
        # *Alpha model; A
        self.CustomAlphaModel = ValueAlphaModel()
        
        # *Portfolio construction model; B
        self.CustomPortfolioConstructionModel = OptimisationPortfolioConstructionModel(turnover=0.05, max_wt=0.05, longshort=True)
        
        #Eexecution model; C
        self.CustomExecution = Execution(liq_tol=0.005)
        
        # *Add SPY for trading days data; a
        self.AddEquity('SPY', Resolution.Daily)
        
        # *Scheduling rebalancing; b ; we take the a daily resloution and at 2 oclock we execute a rebalance 
        self.Schedule.On(self.DateRules.EveryDay('SPY'), self.TimeRules.At(13, 0), Action(self.RebalancePortfolio))
        
        # Init charting
        InitCharts(self)
        
        # Schedule charting
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Friday), self.TimeRules.BeforeMarketClose('SPY', 0), Action(self.PlotCharts))

    def OnData(self, data):
        pass
    
    # this controls the A B C ; we chose when we rebalance; we generate our alpha scores ;we pass the alpha scores into our portfolio construction
    #next we execute orders based on our portfolio construction
    def RebalancePortfolio(self): 
        alpha_df = self.CustomAlphaModel.GenerateAlphaScores(self, self.securities)
        portfolio = self.CustomPortfolioConstructionModel.GenerateOptimalPortfolio(self, alpha_df)
        self.CustomExecution.ExecutePortfolio(self, portfolio)
    
    def PlotCharts(self):
        PlotPerformanceChart(self)
        PlotPosConcentrationChart(self)
        PlotStockCountChart(self)
        PlotExposureChart(self)