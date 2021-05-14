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
SET numcheckins = (SELECT (LENGTH(date) - LENGTH(REPLACE(date, ',', '')) + 1) as numcheck 
                  FROM checkin
               WHERE checkin.business_id = business.business_id)

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