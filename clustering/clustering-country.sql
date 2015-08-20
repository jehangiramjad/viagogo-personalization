------------------------------------------------------------------------------
-- Per Country (for each Event)
select pv4.AnonymousID,  COUNT(DISTINCT e.EventID) as NumberEventsCountry,v.CountryCode, COUNT(DISTINCT pv4.SiteVisitID) as NumberVisitsCountry
from PageVisit.dbo.PageVisit as pv4
cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv4.BrowserAgentID) as isdb4
join viagogo.dbo.Event as e
on pv4.EventID = e.EventID
join viagogo.dbo.Venue as v
on e.VenueID = v.VenueID
where isdb4.IsSelfDeclaredBot = 0
and NOT EXISTS
(
	SELECT
	ip.IP
	FROM
	ViagogoReporting.Report.BotDetectionIPMatch ip
	WHERE
	ip.BotMatchTypeID IN (1,4)
	AND
	ip.IP = pv4.IP
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
    ba.BrowserAgentID = pv4.BrowserAgentID
)
                -- TA: Comparing CategoryID to anything also gets rid of nulls
                --and pv4.CategoryID is not null
                -- TA: Also we're joining PV based on EventId not CategoryId, so the filter below should probably be on event id!
and pv4.isVisitStart = 1
and pv4.CategoryID != 0
and pv4.VisitDate >= '20150401'
and pv4.VisitDate < '20150701'
group by pv4.AnonymousID, v.CountryCode
order by pv4.AnonymousID