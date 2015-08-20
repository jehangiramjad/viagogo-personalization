----------------------------------------------------------------------
---- Events and Visits PER ROOT-CATEGORY
select pv7.AnonymousID, e7.TopLevelCategoryID,  COUNT(DISTINCT e7.EventID) as NumberEventsTopCategory, COUNT(DISTINCT pv7.SiteVisitID) as NumberVisitsTopCategory
from PageVisit.dbo.PageVisit as pv7
cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv7.BrowserAgentID) as isdb7
join viagogo.dbo.Event as e7
on pv7.EventID = e7.EventID
where isdb7.IsSelfDeclaredBot = 0
and NOT EXISTS
(
	SELECT
	ip.IP
	FROM
	ViagogoReporting.Report.BotDetectionIPMatch ip
	WHERE
	ip.BotMatchTypeID IN (1,4)
	AND
	ip.IP = pv7.IP
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
    ba.BrowserAgentID = pv7.BrowserAgentID
)
and pv7.isVisitStart = 1
and pv7.CategoryID != 0
and pv7.VisitDate >= '20150401'
and pv7.VisitDate < '20150701'
group by pv7.AnonymousID, e7.TopLevelCategoryID
order by pv7.AnonymousID