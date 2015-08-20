----------------------------------------------------------------------
---- Events and Visits FOR MONTHS
select temp.AnonymousID, temp.EventMonth, COUNT(DISTINCT temp.EventID) as NumberEventsMonth, COUNT(DISTINCT temp.SiteVisitID) as NumberVisitsMonth
from
(
select pv8.AnonymousID, DATEPART(MM, e8.EventDateTime) as EventMonth, pv8.SiteVisitID, e8.EventID
from PageVisit.dbo.PageVisit as pv8
cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv8.BrowserAgentID) as isdb8
join viagogo.dbo.Event as e8
on pv8.EventID = e8.EventID
where isdb8.IsSelfDeclaredBot = 0
and NOT EXISTS
(
	SELECT
	ip.IP
	FROM
	ViagogoReporting.Report.BotDetectionIPMatch ip
	WHERE
	ip.BotMatchTypeID IN (1,4)
	AND
	ip.IP = pv8.IP
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
    ba.BrowserAgentID = pv8.BrowserAgentID
)
and pv8.isVisitStart = 1
and pv8.CategoryID != 0
and pv8.VisitDate >= '20150401'
and pv8.VisitDate < '20150701'
) as temp
group by temp.AnonymousID, temp.EventMonth
order by temp.AnonymousID