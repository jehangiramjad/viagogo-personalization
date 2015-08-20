-----------------------------------------------------------------
-- TOTAL VISITS and AVERAGE TICKET PRICE, Number of Transactions, Number of FanOfEmails
select 
	pv5.AnonymousID,  
	COUNT(DISTINCT e5.EventID) as NumberEventsTotal, 
	COUNT(DISTINCT pv5.SiteVisitID) as NumberVisitsTotal, 
	avg(l5.DefaultCurrentPrice / c.CurrencyRate) as AveragePriceEUR,
	COUNT(DISTINCT t5.TransactionID) as NumberTransactions,
	COUNT(DISTINCT foce5.CategoryID) as NumberFanOfCategories
from PageVisit.dbo.PageVisit as pv5
cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv5.BrowserAgentID) as isdb5
join viagogo.dbo.Event as e5
on pv5.EventID = e5.EventID
join viagogo.dbo.Listing as l5
on l5.EventID = e5.EventID
cross apply
(
      select top 1 CurrencyRate
      from viagogo.dbo.CurrencyRate as cr
      where cr.CurrencyCode = l5.CurrencyCode
) as c
left join viagogo.dbo.[Transaction] as t5
on try_cast(t5.SessionID as uniqueidentifier) = pv5.SiteVisitID
left join ViagogoReporting.dbo.TransactionDetail as td5
on (t5.TransactionID = td5.TransactionID AND td5.isValidTransaction = 1)
left join viagogo.dbo.EmailEmailSource as ees5
on pv5.SiteVisitID = try_cast(ees5.SessionID as uniqueIdentifier)
left join viagogo.dbo.FanOfCategoryEmail as foce5
on ees5.EmailID = foce5.EmailID
where e5.IsActive = 1
and isdb5.IsSelfDeclaredBot = 0
and NOT EXISTS
(
	SELECT
	ip.IP
	FROM
	ViagogoReporting.Report.BotDetectionIPMatch ip
	WHERE
	ip.BotMatchTypeID IN (1,4)
	AND
	ip.IP = pv5.IP
)
and NOT EXISTS
(
    SELECT
    ba.BrowserAgentID
    FROM
    ViagogoReporting.Report.BotDetectionBrowserAgentMatch ba
    WHERE
    ba.BotMatchTypeID IN (1,4)
    AND
    ba.BrowserAgentID = pv5.BrowserAgentID
)
and pv5.isVisitStart = 1
and pv5.CategoryID != 0
and pv5.VisitDate >= '20150401'
and pv5.VisitDate < '20150701'
group by pv5.AnonymousID
order by pv5.AnonymousID
