--teamwaffleiron72x_UPDATE.sql
--tipcount to business:
UPDATE business
SET tipcount = (select count(tip.user_id) 
               FROM tip, usertable 
               WHERE tip.business_id = business.business_id
               AND usertable.user_id = tip.user_id)
;

--tipcount to usertable
UPDATE usertable
SET tipcount = (select count(tip.user_id) 
               FROM tip, business
               WHERE tip.user_id = usertable.user_id
AND tip.business_id = business.business_id)
;


--totallikes to user table
UPDATE usertable
SET totallikes = (select sum(tip.likes) 
               FROM tip 
               WHERE tip.user_id = usertable.user_id)
;

--numcheckins to business


UPDATE business
set numcheckins = numcheck
FROM (SELECT business.business_id as id, count(business.business_id) as numcheck 
                  FROM checkin, business
               WHERE checkin.business_id = business.business_id
GROUP BY 1) as a
WHERE business.business_id = a.id

;


--totallikes to business:
UPDATE business
SET totallikes = (select sum(tip.likes) 
               FROM tip 
               WHERE tip.business_id = business.business_id)
;
--numtips to business:
UPDATE business
SET numtips = (select count(*) 
               FROM tip 
               WHERE tip.business_id = business.business_id)
;
