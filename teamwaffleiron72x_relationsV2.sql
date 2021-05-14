CREATE TABLE business	(
	business_id VARCHAR,
	name VARCHAR,
	address VARCHAR,
	city VARCHAR,
	state VARCHAR,
	postal_code VARCHAR,
	latitude FLOAT,
	longitude FLOAT,
	stars VARCHAR,
	review_count INTEGER,
	is_open BOOL,
	numTips INTEGER DEFAULT 0,
	numCheckins INTEGER DEFAULT 0,
	totallikes INTEGER DEFAULT 0,
	tipcount INTEGER DEFAULT 0,
	PRIMARY KEY (business_id)
)
;

CREATE TABLE usertable(
	average_stars DECIMAL(4,2),
	cool INTEGER,
	fans INTEGER,
	friends TEXT,
	funny INTEGER,
	name VARCHAR,
	tipcount INTEGER,
	useful INTEGER,
	user_id VARCHAR,
	yelping_since DATE,
	longitude FLOAT,
	latitude FLOAT,
	PRIMARY KEY (user_id)
)
;

CREATE TABLE checkin(
	business_id VARCHAR,
	date VARCHAR,
	PRIMARY KEY (business_id, date),
	FOREIGN KEY (business_id) REFERENCES business(business_id)
)
;

CREATE TABLE hours(
	business_id VARCHAR,
	day VARCHAR,
	open TIME,
	close TIME,
	PRIMARY KEY (business_id),
	FOREIGN KEY(business_id) REFERENCES business(business_id)
)
;

CREATE TABLE category(
	business_id VARCHAR,
	category VARCHAR,
	PRIMARY KEY (business_id, category),
	FOREIGN KEY (business_id) REFERENCES business(business_id)
)
;

CREATE TABLE attribute(
	business_id VARCHAR,
	name VARCHAR,
	value BOOL,
	PRIMARY KEY (business_id, name),
	FOREIGN KEY (business_id) REFERENCES business(business_id)
)
;




CREATE TABLE friends(
	user_id VARCHAR,
	friend_user_id VARCHAR,
	PRIMARY KEY(user_id, friend_user_id),
	FOREIGN KEY(user_id) REFERENCES usertable(user_id),
	FOREIGN KEY(friend_user_id) REFERENCES usertable(user_id)
)
;

--ignore this one
--CREATE TABLE tip(
--	user_id VARCHAR,
--	tipdate VARCHAR,
--	likes INTEGER,
--	tiptext TEXT,
--	PRIMARY KEY (user_id),
--	FOREIGN KEY (user_id) REFERENCES usertable(user_id)
--)
--;


--fixed tip table
CREATE TABLE tip(
	business_id VARCHAR,
	date VARCHAR,
	likes INTEGER,
	text TEXT,
	user_id VARCHAR,
	PRIMARY KEY (business_id, user_id, date),
	FOREIGN KEY (business_id) REFERENCES business(business_id),
	FOREIGN KEY (user_id) REFERENCES usertable(user_id)
)
;
CREATE TABLE belong(
	user_id VARCHAR,
	date VARCHAR,
	business_id VARCHAR,
	PRIMARY KEY (user_id, date, business_id),
	FOREIGN KEY (user_id, date, business_id) REFERENCES tip(user_id, date, business_id),
	FOREIGN KEY (user_id) REFERENCES usertable(user_id),
	FOREIGN KEY (business_id) REFERENCES business(business_id)
)
;