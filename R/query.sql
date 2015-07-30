-- COMBINED QUERY
select subOut.AnonymousID, subOut.CategoryID, MAX(subOut.LevelInterest)
 
-- Subquery
from (
 -- TRANSACTION MADE (Level of Interest = 5)
-- GROUPED by AnonID (row) and CategoryID (columns)
	select pv.AnonymousID, ev.CategoryID, 5 as LevelInterest
	from viagogo.dbo.[Transaction] as t
	join PageVisit.dbo.PageVisit as pv
	on try_cast(t.SessionID as uniqueidentifier) = pv.SiteVisitID
	and pv.IsVisitStart = 1
	join ViagogoReporting.dbo.TransactionDetail as td
	on t.TransactionID = td.TransactionID
	cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv.BrowserAgentID) as isdb
	join viagogo.dbo.EventCategory as ev
	on t.EventID = ev.EventID
	and isdb.IsSelfDeclaredBot = 0
	and NOT EXISTS
	(
	SELECT ip.IP
	FROM ViagogoReporting.Report.BotDetectionIPMatch ip
	WHERE ip.BotMatchTypeID IN (1,4)
	AND ip.IP = pv.IP
	)
	and NOT EXISTS
	(
	SELECT ba.BrowserAgentID
	FROM ViagogoReporting.Report.BotDetectionBrowserAgentMatch ba
	WHERE ba.BotMatchTypeID IN (1,4)
	AND ba.BrowserAgentID = pv.BrowserAgentID
	)
	and td.isValidTransaction = 1
	and pv.VisitDate >= '20150401'
	and pv.VisitDate < '20150701'
	group by pv.AnonymousID, ev.categoryID
 
	UNION 
 
                --CHECKOUT PROCESS STARTED (Level of Interest = 3)
                -- AnonID (row), CategoryID (column)
                select pv2.AnonymousID, ev2.CategoryID as CategoryID, 3 as LevelInterest 
                from PageEvent.dbo.Pipeline as pp2
                join viagogo.dbo.EventCategory as ev2
                on pp2.EventID = ev2.EventId
                join PageVisit.dbo.PageVisit as pv2
                on pv2.PageVisitID = pp2.PageVisitID
                cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv2.BrowserAgentID) as isdb2              
                
                --from PageVisit.dbo.PageVisit as pv2
                --cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv2.BrowserAgentID) as isdb2
                --join PageEvent.dbo.Pipeline as pp2
                --on pv2.SiteVisitID = pp2.SiteVisitID
                --join viagogo.dbo.EventCategory as ev2
                --on pv2.EventID = ev2.EventID
                where isdb2.IsSelfDeclaredBot = 0
                and NOT EXISTS
                (
                                SELECT
                                ip.IP
                                FROM
                                ViagogoReporting.Report.BotDetectionIPMatch ip
                                WHERE
                                ip.BotMatchTypeID IN (1,4)
                                AND
                                ip.IP = pv2.IP
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
                                ba.BrowserAgentID = pv2.BrowserAgentID
                )
                and pv2.VisitDate >= '20150401'
                and pv2.VisitDate < '20150701'
                and pv2.AnonymousID is not null
                and pp2.EntryDateTime >= '20150401'
                and pp2.EntryDateTime < '20150701'
                group by pv2.AnonymousID, ev2.CategoryID
                UNION
 
                -- SIMPLY VIEWING THE EVENT (only once: Level of Interest = 1, more than once: Level of Interest = 2)
                -- AnonID (row), CategoryID (column)
                select pv4.AnonymousID, ev4.CategoryID,
                CASE 
                --TA: count(*) would be enough here as it's vanishingly unlikely the user visited the same page twice in the same millisecond
                when  --count(distinct pv4.VisitDate) > 1 then 2
                                                count(*) > 1 then 2
                else 1
                END as LevelInterest
                from PageVisit.dbo.PageVisit as pv4
                cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv4.BrowserAgentID) as isdb4
                join viagogo.dbo.EventCategory as ev4
                on pv4.EventID = ev4.EventID
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
                and pv4.CategoryID != 0
                and pv4.VisitDate >= '20150401'
                and pv4.VisitDate < '20150701'
                group by pv4.AnonymousID, ev4.CategoryID
 
                UNION
 
                -- FAN OF CATEGORY: Level of Interest = 4
                -- AnonID (row), CategoryID (column)
                -- NOTE: This has no filter for the Date of Visit since this info is assumed to be more persistent
                select pv3.AnonymousID, foce.CategoryID, 4 as LevelInterest
                from PageVisit.dbo.PageVisit as pv3
                cross apply ViagogoReporting.report.IsSelfDeclaredBot(pv3.BrowserAgentID) as isdb3
                join viagogo.dbo.EmailEmailSource as ees
                on pv3.SiteVisitID = try_cast(ees.SessionID as uniqueIdentifier)
				and pv3.IsVisitStart = 1
                join viagogo.dbo.FanOfCategoryEmail as foce
                on ees.EmailID = foce.EmailID
                -- TA: This join was just inflating results [every event linked to the category would show up for every category Id in FOCE]
                --join viagogo.dbo.EventCategory as ev3
                --on foce.CategoryID = ev3.CategoryID
                where isdb3.IsSelfDeclaredBot = 0
                and NOT EXISTS
                (
                                SELECT
                                ip.IP
                                FROM
                                ViagogoReporting.Report.BotDetectionIPMatch ip
                                WHERE
                                ip.BotMatchTypeID IN (1,4)
                                AND
                                ip.IP = pv3.IP
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
                                ba.BrowserAgentID = pv3.BrowserAgentID
                )
                -- TA: Filter out the useless data early
                and try_cast(ees.SessionID as uniqueidentifier) is not null
                and pv3.AnonymousID is not null
                group by pv3.AnonymousID, foce.CategoryID
                ) as subOut
 
join 
(
                SELECT lcp1.CategoryID
                FROM viagogo.dbo.LeafCategoryParent lcp1
                WHERE lcp1.[Level] = 0
                --AND lcp1.GeographyID = 1
                AND EXISTS (
                                SELECT lcp2.CategoryID
                                FROM viagogo.dbo.LeafCategoryParent lcp2
                                WHERE lcp2.CategoryID = lcp1.CategoryID
                                AND lcp2.ParentCategoryID = 0 -- Not sport
                                                --OR lcp2.ParentCategoryID = 3
                                                --OR lcp2.ParentCategoryID = 1023)
                                --0 = All / 1 = Theatre / 2 = Sport / 3 = Concert / 1023 = Festival
                                --AND lcp2.GeographyID = 1
                )
                group by lcp1.CategoryID
) as leafCat
on subOut.CategoryID = leafCat.CategoryID
 
group by subOut.AnonymousID, subOut.CategoryID
