--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.18 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: billstatus; Type: TYPE; Schema: public; Owner: ashishtandon
--

CREATE TYPE public.billstatus AS ENUM (
    'INTRODUCED',
    'FIRST_READING',
    'SECOND_READING',
    'COMMITTEE',
    'THIRD_READING',
    'PASSED',
    'ROYAL_ASSENT',
    'FAILED',
    'WITHDRAWN'
);


ALTER TYPE public.billstatus OWNER TO ashishtandon;

--
-- Name: eventtype; Type: TYPE; Schema: public; Owner: ashishtandon
--

CREATE TYPE public.eventtype AS ENUM (
    'MEETING',
    'VOTE',
    'READING',
    'COMMITTEE_MEETING',
    'OTHER'
);


ALTER TYPE public.eventtype OWNER TO ashishtandon;

--
-- Name: jurisdictiontype; Type: TYPE; Schema: public; Owner: ashishtandon
--

CREATE TYPE public.jurisdictiontype AS ENUM (
    'FEDERAL',
    'PROVINCIAL',
    'MUNICIPAL'
);


ALTER TYPE public.jurisdictiontype OWNER TO ashishtandon;

--
-- Name: representativerole; Type: TYPE; Schema: public; Owner: ashishtandon
--

CREATE TYPE public.representativerole AS ENUM (
    'MP',
    'MPP',
    'MLA',
    'MNA',
    'MAYOR',
    'COUNCILLOR',
    'REEVE',
    'OTHER'
);


ALTER TYPE public.representativerole OWNER TO ashishtandon;

--
-- Name: voteresult; Type: TYPE; Schema: public; Owner: ashishtandon
--

CREATE TYPE public.voteresult AS ENUM (
    'YES',
    'NO',
    'ABSTAIN',
    'ABSENT'
);


ALTER TYPE public.voteresult OWNER TO ashishtandon;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bill_sponsorships; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.bill_sponsorships (
    id uuid NOT NULL,
    bill_id uuid NOT NULL,
    representative_id uuid NOT NULL,
    is_primary_sponsor boolean,
    sponsorship_type character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.bill_sponsorships OWNER TO ashishtandon;

--
-- Name: bills; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.bills (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    bill_number character varying(50) NOT NULL,
    title character varying(500) NOT NULL,
    summary text,
    full_text text,
    status public.billstatus NOT NULL,
    introduced_date timestamp without time zone,
    first_reading_date timestamp without time zone,
    second_reading_date timestamp without time zone,
    third_reading_date timestamp without time zone,
    passed_date timestamp without time zone,
    royal_assent_date timestamp without time zone,
    legislative_body character varying(100),
    source_url character varying(500),
    external_id character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.bills OWNER TO ashishtandon;

--
-- Name: committee_memberships; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.committee_memberships (
    id uuid NOT NULL,
    committee_id uuid NOT NULL,
    representative_id uuid NOT NULL,
    role character varying(100),
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.committee_memberships OWNER TO ashishtandon;

--
-- Name: committees; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.committees (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    committee_type character varying(100),
    source_url character varying(500),
    external_id character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.committees OWNER TO ashishtandon;

--
-- Name: data_collection_tracking; Type: TABLE; Schema: public; Owner: openpolicy
--

CREATE TABLE public.data_collection_tracking (
    id integer NOT NULL,
    scraper_name character varying(255) NOT NULL,
    scraper_path character varying(500) NOT NULL,
    status character varying(50) NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    records_collected integer DEFAULT 0,
    records_stored integer DEFAULT 0,
    error_message text,
    data_size_bytes bigint DEFAULT 0,
    collection_duration_seconds double precision DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.data_collection_tracking OWNER TO openpolicy;

--
-- Name: data_collection_tracking_id_seq; Type: SEQUENCE; Schema: public; Owner: openpolicy
--

CREATE SEQUENCE public.data_collection_tracking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_collection_tracking_id_seq OWNER TO openpolicy;

--
-- Name: data_collection_tracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openpolicy
--

ALTER SEQUENCE public.data_collection_tracking_id_seq OWNED BY public.data_collection_tracking.id;


--
-- Name: data_quality_issues; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.data_quality_issues (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    issue_type character varying(100) NOT NULL,
    severity character varying(20) NOT NULL,
    description text NOT NULL,
    affected_table character varying(100),
    affected_record_id character varying(100),
    detected_at timestamp without time zone NOT NULL,
    resolved_at timestamp without time zone,
    resolution_notes text
);


ALTER TABLE public.data_quality_issues OWNER TO ashishtandon;

--
-- Name: events; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.events (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    bill_id uuid,
    committee_id uuid,
    name character varying(255) NOT NULL,
    description text,
    event_type public.eventtype NOT NULL,
    event_date timestamp without time zone NOT NULL,
    location character varying(255),
    source_url character varying(500),
    external_id character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.events OWNER TO ashishtandon;

--
-- Name: jurisdictions; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.jurisdictions (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    jurisdiction_type public.jurisdictiontype NOT NULL,
    division_id character varying(255),
    province character varying(2),
    url character varying(500),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.jurisdictions OWNER TO ashishtandon;

--
-- Name: representatives; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.representatives (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    role public.representativerole NOT NULL,
    party character varying(100),
    district character varying(255),
    email character varying(255),
    phone character varying(50),
    office_address text,
    website character varying(500),
    facebook_url character varying(500),
    twitter_url character varying(500),
    instagram_url character varying(500),
    linkedin_url character varying(500),
    term_start timestamp without time zone,
    term_end timestamp without time zone,
    photo_url character varying(500),
    biography text,
    source_url character varying(500),
    external_id character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.representatives OWNER TO ashishtandon;

--
-- Name: scraping_runs; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.scraping_runs (
    id uuid NOT NULL,
    jurisdiction_id uuid NOT NULL,
    run_type character varying(50) NOT NULL,
    status character varying(50) NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    records_processed integer,
    records_created integer,
    records_updated integer,
    errors_count integer,
    error_log json,
    summary json,
    created_at timestamp without time zone
);


ALTER TABLE public.scraping_runs OWNER TO ashishtandon;

--
-- Name: votes; Type: TABLE; Schema: public; Owner: ashishtandon
--

CREATE TABLE public.votes (
    id uuid NOT NULL,
    event_id uuid NOT NULL,
    bill_id uuid,
    representative_id uuid NOT NULL,
    vote_result public.voteresult NOT NULL,
    vote_date timestamp without time zone NOT NULL,
    source_url character varying(500),
    created_at timestamp without time zone
);


ALTER TABLE public.votes OWNER TO ashishtandon;

--
-- Name: data_collection_tracking id; Type: DEFAULT; Schema: public; Owner: openpolicy
--

ALTER TABLE ONLY public.data_collection_tracking ALTER COLUMN id SET DEFAULT nextval('public.data_collection_tracking_id_seq'::regclass);


--
-- Data for Name: bill_sponsorships; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.bill_sponsorships (id, bill_id, representative_id, is_primary_sponsor, sponsorship_type, created_at) FROM stdin;
\.


--
-- Data for Name: bills; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.bills (id, jurisdiction_id, bill_number, title, summary, full_text, status, introduced_date, first_reading_date, second_reading_date, third_reading_date, passed_date, royal_assent_date, legislative_body, source_url, external_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: committee_memberships; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.committee_memberships (id, committee_id, representative_id, role, start_date, end_date, created_at) FROM stdin;
\.


--
-- Data for Name: committees; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.committees (id, jurisdiction_id, name, description, committee_type, source_url, external_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: data_collection_tracking; Type: TABLE DATA; Schema: public; Owner: openpolicy
--

COPY public.data_collection_tracking (id, scraper_name, scraper_path, status, start_time, end_time, records_collected, records_stored, error_message, data_size_bytes, collection_duration_seconds, created_at) FROM stdin;
\.


--
-- Data for Name: data_quality_issues; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.data_quality_issues (id, jurisdiction_id, issue_type, severity, description, affected_table, affected_record_id, detected_at, resolved_at, resolution_notes) FROM stdin;
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.events (id, jurisdiction_id, bill_id, committee_id, name, description, event_type, event_date, location, source_url, external_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: jurisdictions; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.jurisdictions (id, name, jurisdiction_type, division_id, province, url, created_at, updated_at) FROM stdin;
48d4cd4d-c28c-44bf-887a-1a76948e3c04	Canada	FEDERAL	ocd-division/country:ca	\N	https://www.ourcommons.ca/	2025-08-01 15:49:44.178363	2025-08-01 15:49:44.17837
b16f6a2e-aecc-42a6-9489-b4af12132e45	Ontario	PROVINCIAL	ocd-division/country:ca/province:on	ON	\N	2025-08-01 15:49:44.178374	2025-08-01 15:49:44.178374
13cb3334-399c-4bdc-8057-249d5ad84a43	Saskatchewan	PROVINCIAL	ocd-division/country:ca/province:sk	SK	\N	2025-08-01 15:49:44.178377	2025-08-01 15:49:44.178378
7befb211-81d7-49ba-ba4c-ad141e16397f	Prince Edward Island	PROVINCIAL	ocd-division/country:ca/province:pe	PE	\N	2025-08-01 15:49:44.17838	2025-08-01 15:49:44.178381
deff1546-0280-4f9b-b2c4-1044a7be054a	Northwest Territories	PROVINCIAL	ocd-division/country:ca/province:nt	NT	\N	2025-08-01 15:49:44.178383	2025-08-01 15:49:44.178383
25088de0-17d4-4c8f-9618-19260777668a	Alberta	PROVINCIAL	ocd-division/country:ca/province:ab	AB	\N	2025-08-01 15:49:44.178386	2025-08-01 15:49:44.178386
8afce970-efbc-478f-9f1b-f02e4ed3070f	Newfoundland and Labrador	PROVINCIAL	ocd-division/country:ca/province:nl	NL	\N	2025-08-01 15:49:44.178388	2025-08-01 15:49:44.178389
3c46f372-5253-404d-aa2c-2f4542863fc7	Yukon	PROVINCIAL	ocd-division/country:ca/province:yt	YT	\N	2025-08-01 15:49:44.178391	2025-08-01 15:49:44.178391
d6138224-762f-4ce5-a228-e3f969394072	Quebec	PROVINCIAL	ocd-division/country:ca/province:qc	QC	\N	2025-08-01 15:49:44.178393	2025-08-01 15:49:44.178394
d24464a6-131b-49d6-83e0-d4e3d91cf9f7	Manitoba	PROVINCIAL	ocd-division/country:ca/province:mb	MB	\N	2025-08-01 15:49:44.178396	2025-08-01 15:49:44.178396
7d813296-0b9d-4421-9f7f-f958cf3493e0	British Columbia	PROVINCIAL	ocd-division/country:ca/province:bc	BC	\N	2025-08-01 15:49:44.178398	2025-08-01 15:49:44.178399
aa15ee22-df1d-46eb-800c-cdd4b8bc8a4c	Nova Scotia	PROVINCIAL	ocd-division/country:ca/province:ns	NS	\N	2025-08-01 15:49:44.178401	2025-08-01 15:49:44.178401
2108fe8e-0fea-4588-b63b-61f36d457c19	Nunavut	PROVINCIAL	ocd-division/country:ca/province:nu	NU	\N	2025-08-01 15:49:44.178403	2025-08-01 15:49:44.178404
ffd2f321-8a3d-456b-9451-72fcb1ff3810	New Brunswick	PROVINCIAL	ocd-division/country:ca/province:nb	NB	\N	2025-08-01 15:49:44.178406	2025-08-01 15:49:44.178406
78881584-f3fd-419a-b6e9-4417f085d454	Fredericton	MUNICIPAL	ocd-division/country:ca/province:nb/municipality:fredericton	NB	\N	2025-08-01 15:49:44.178408	2025-08-01 15:49:44.178408
bb165b3a-f092-481d-98fd-1528c29a52d1	Winnipeg	MUNICIPAL	ocd-division/country:ca/province:mb/municipality:winnipeg	MB	\N	2025-08-01 15:49:44.17841	2025-08-01 15:49:44.178411
13de6eca-f21c-43b4-b430-b70690f820cc	Moncton	MUNICIPAL	ocd-division/country:ca/province:nb/municipality:moncton	NB	\N	2025-08-01 15:49:44.178413	2025-08-01 15:49:44.178413
4ef764a0-51a9-4bdb-a4ae-b6264d23fb37	Ajax	MUNICIPAL	ocd-division/country:ca/province:on/municipality:ajax	ON	\N	2025-08-01 15:49:44.178415	2025-08-01 15:49:44.178416
ad7291c5-f4d1-4fe9-9023-7428b83b0b1f	New Westminster	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:new_westminster	BC	\N	2025-08-01 15:49:44.178418	2025-08-01 15:49:44.178418
d09142d1-11f1-4a07-97fa-580010b6f12a	Cambridge	MUNICIPAL	ocd-division/country:ca/province:on/municipality:cambridge	ON	\N	2025-08-01 15:49:44.17842	2025-08-01 15:49:44.178421
b15f588c-4493-4cfc-8c89-e28854f31884	London	MUNICIPAL	ocd-division/country:ca/province:on/municipality:london	ON	\N	2025-08-01 15:49:44.178423	2025-08-01 15:49:44.178423
b3f28271-ef5b-4433-a288-755c7d6e68f2	Kawartha Lakes	MUNICIPAL	ocd-division/country:ca/province:on/municipality:kawartha_lakes	ON	\N	2025-08-01 15:49:44.178425	2025-08-01 15:49:44.178426
bd8902eb-6319-47b7-a48c-bbe09085e6db	Saint John	MUNICIPAL	ocd-division/country:ca/province:nb/municipality:saint_john	NB	\N	2025-08-01 15:49:44.178428	2025-08-01 15:49:44.178428
73bd1b27-03c9-40e1-97ef-dd06fcaa9d51	Richmond	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:richmond	BC	\N	2025-08-01 15:49:44.17843	2025-08-01 15:49:44.178431
e251630f-d18a-451b-85fc-ffeeb863130d	Kelowna	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:kelowna	BC	\N	2025-08-01 15:49:44.178433	2025-08-01 15:49:44.178433
bceec29a-43e0-4c69-9ee4-184e11f43c42	Hamilton	MUNICIPAL	ocd-division/country:ca/province:on/municipality:hamilton	ON	\N	2025-08-01 15:49:44.178435	2025-08-01 15:49:44.178436
184e02f2-c2aa-453a-8853-7351a755f984	Toronto	MUNICIPAL	ocd-division/country:ca/province:on/municipality:toronto	ON	\N	2025-08-01 15:49:44.178438	2025-08-01 15:49:44.178438
db17286f-cd93-4391-996f-343aa4528be2	Surrey	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:surrey	BC	\N	2025-08-01 15:49:44.17844	2025-08-01 15:49:44.178441
1c165b31-6728-4b35-a4c4-d7767611a0fe	Waterloo	MUNICIPAL	ocd-division/country:ca/province:on/municipality:waterloo	ON	\N	2025-08-01 15:49:44.178443	2025-08-01 15:49:44.178443
91fcc542-21fe-4c5b-8713-45a2cfcec4a5	Lambton	MUNICIPAL	ocd-division/country:ca/province:on/municipality:lambton	ON	\N	2025-08-01 15:49:44.178445	2025-08-01 15:49:44.178446
b0f138b3-d9a0-4f4c-b394-6192666f2d20	Caledon	MUNICIPAL	ocd-division/country:ca/province:on/municipality:caledon	ON	\N	2025-08-01 15:49:44.178448	2025-08-01 15:49:44.178448
4357c03e-96a8-4ccb-9dcf-966c961d59c1	Burnaby	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:burnaby	BC	\N	2025-08-01 15:49:44.17845	2025-08-01 15:49:44.178451
3c4b62a4-bff3-40a4-af11-1245dd0cb8c1	Pickering	MUNICIPAL	ocd-division/country:ca/province:on/municipality:pickering	ON	\N	2025-08-01 15:49:44.178453	2025-08-01 15:49:44.178453
b3374b88-f4f2-42d2-968a-75466a3134e2	Stratford	MUNICIPAL	ocd-division/country:ca/province:pe/municipality:stratford	PE	\N	2025-08-01 15:49:44.178455	2025-08-01 15:49:44.178455
62ba83f7-acd5-4ff4-ae0c-7d84c7bd95bc	Laval	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:laval	QC	\N	2025-08-01 15:49:44.178457	2025-08-01 15:49:44.178458
f96fb763-da1b-4fee-a6a6-60119b560052	Haldimand County	MUNICIPAL	ocd-division/country:ca/province:on/municipality:haldimand_county	ON	\N	2025-08-01 15:49:44.17846	2025-08-01 15:49:44.17846
995040e5-fc6b-4cc6-b640-336a3e841651	Oakville	MUNICIPAL	ocd-division/country:ca/province:on/municipality:oakville	ON	\N	2025-08-01 15:49:44.178462	2025-08-01 15:49:44.178463
19f6ad23-ead3-425d-9b08-c8324ea20f98	Grande Prairie County No 1	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:grande_prairie_county_no_1	AB	\N	2025-08-01 15:49:44.178465	2025-08-01 15:49:44.178465
541297f2-36da-41bc-ad8a-b8a7d1303d7f	Dollard Des Ormeaux	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:dollard_des_ormeaux	QC	\N	2025-08-01 15:49:44.178467	2025-08-01 15:49:44.178468
2d32b8ea-f861-41b5-871a-8368b2e0badf	Sainte Anne De Bellevue	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:sainte_anne_de_bellevue	QC	\N	2025-08-01 15:49:44.17847	2025-08-01 15:49:44.17847
10be238d-feac-4367-a3e4-f77664cc8e34	Victoria	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:victoria	BC	\N	2025-08-01 15:49:44.178472	2025-08-01 15:49:44.178473
f0f9db9c-7456-4bf8-8438-730198b0cff4	Coquitlam	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:coquitlam	BC	\N	2025-08-01 15:49:44.178475	2025-08-01 15:49:44.178475
36829e96-ab4c-4cd7-88ee-de5a2c03c32f	Peel	MUNICIPAL	ocd-division/country:ca/province:on/municipality:peel	ON	\N	2025-08-01 15:49:44.178477	2025-08-01 15:49:44.178477
ccc3efd1-2d9b-4f2b-ad78-f35691e16910	Levis	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:levis	QC	\N	2025-08-01 15:49:44.178479	2025-08-01 15:49:44.17848
a8399402-5a01-485d-a025-49ccd7cf52e5	Newmarket	MUNICIPAL	ocd-division/country:ca/province:on/municipality:newmarket	ON	\N	2025-08-01 15:49:44.178482	2025-08-01 15:49:44.178482
1a8b1cf8-8b7d-4f9b-b2b6-7f425d25151e	Kitchener	MUNICIPAL	ocd-division/country:ca/province:on/municipality:kitchener	ON	\N	2025-08-01 15:49:44.178484	2025-08-01 15:49:44.178485
d5cdcc25-463a-43dd-bd55-41fb6076d5c5	Waterloo Region	MUNICIPAL	ocd-division/country:ca/province:on/municipality:waterloo_region	ON	\N	2025-08-01 15:49:44.178487	2025-08-01 15:49:44.178487
8b25a014-0d20-4e76-9c9d-663a46511203	Sherbrooke	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:sherbrooke	QC	\N	2025-08-01 15:49:44.178489	2025-08-01 15:49:44.17849
6593ceda-331c-4412-aa81-55715eb81742	Niagara	MUNICIPAL	ocd-division/country:ca/province:on/municipality:niagara	ON	\N	2025-08-01 15:49:44.178492	2025-08-01 15:49:44.178492
54130970-9175-49e3-b3b0-e410a73e92e9	Langley City	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:langley_city	BC	\N	2025-08-01 15:49:44.178494	2025-08-01 15:49:44.178495
ebb5daad-933b-483f-b941-92e753c810b2	Halifax	MUNICIPAL	ocd-division/country:ca/province:ns/municipality:halifax	NS	\N	2025-08-01 15:49:44.178497	2025-08-01 15:49:44.178497
b663b44a-94c4-4bb5-8c8e-b34cadd6dd13	Terrebonne	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:terrebonne	QC	\N	2025-08-01 15:49:44.178499	2025-08-01 15:49:44.1785
07f8d32b-f7d1-4a36-b775-ccd5080f44d9	Clarington	MUNICIPAL	ocd-division/country:ca/province:on/municipality:clarington	ON	\N	2025-08-01 15:49:44.178502	2025-08-01 15:49:44.178502
dfd8ad6b-6596-4b3f-a416-b601376f9900	St Catharines	MUNICIPAL	ocd-division/country:ca/province:on/municipality:st_catharines	ON	\N	2025-08-01 15:49:44.178504	2025-08-01 15:49:44.178504
86760945-20b1-44bc-9687-c18754aee5be	Fort Erie	MUNICIPAL	ocd-division/country:ca/province:on/municipality:fort_erie	ON	\N	2025-08-01 15:49:44.178507	2025-08-01 15:49:44.178507
7994b3ba-7b3f-4ab5-8cc4-2ef33f37cdd0	Huron	MUNICIPAL	ocd-division/country:ca/province:on/municipality:huron	ON	\N	2025-08-01 15:49:44.178509	2025-08-01 15:49:44.178509
4545c9a3-8269-4514-b3f5-d682a3ace1a2	Guelph	MUNICIPAL	ocd-division/country:ca/province:on/municipality:guelph	ON	\N	2025-08-01 15:49:44.178511	2025-08-01 15:49:44.178512
9d7d46e3-b788-4df6-ae4b-3da6e2b4426a	King	MUNICIPAL	ocd-division/country:ca/province:on/municipality:king	ON	\N	2025-08-01 15:49:44.178514	2025-08-01 15:49:44.178514
3ca68a98-8014-4509-b856-4a9ef650fe70	Brossard	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:brossard	QC	\N	2025-08-01 15:49:44.178516	2025-08-01 15:49:44.178517
32459ed6-95df-443e-97f3-0f9de3546a9e	Windsor	MUNICIPAL	ocd-division/country:ca/province:on/municipality:windsor	ON	\N	2025-08-01 15:49:44.178519	2025-08-01 15:49:44.178519
a2586a8d-36c0-4a35-8548-41989a7045c1	Niagara On The Lake	MUNICIPAL	ocd-division/country:ca/province:on/municipality:niagara_on_the_lake	ON	\N	2025-08-01 15:49:44.178521	2025-08-01 15:49:44.178522
48ac51c4-6f59-4b11-b5d2-a10b915be57d	Belleville	MUNICIPAL	ocd-division/country:ca/province:on/municipality:belleville	ON	\N	2025-08-01 15:49:44.178524	2025-08-01 15:49:44.178524
8b2d1dae-d946-4677-b0a9-997827e3bf8b	Westmount	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:westmount	QC	\N	2025-08-01 15:49:44.178526	2025-08-01 15:49:44.178526
c6835884-df26-4ff3-947f-1a67fea48b42	Longueuil	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:longueuil	QC	\N	2025-08-01 15:49:44.178528	2025-08-01 15:49:44.178529
bdc682fd-0526-4136-b414-d3a25f9a163a	Saguenay	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:saguenay	QC	\N	2025-08-01 15:49:44.178531	2025-08-01 15:49:44.178531
d43f5fbd-af55-4d5c-aaa8-884181cd1759	Vaughan	MUNICIPAL	ocd-division/country:ca/province:on/municipality:vaughan	ON	\N	2025-08-01 15:49:44.178533	2025-08-01 15:49:44.178534
8436445e-4c1f-45f4-969a-565a3fe0f9c4	Whitchurch Stouffville	MUNICIPAL	ocd-division/country:ca/province:on/municipality:whitchurch_stouffville	ON	\N	2025-08-01 15:49:44.178536	2025-08-01 15:49:44.178536
0d6c2534-eede-4b08-9f73-7f860b7ee578	Brampton	MUNICIPAL	ocd-division/country:ca/province:on/municipality:brampton	ON	\N	2025-08-01 15:49:44.178538	2025-08-01 15:49:44.178538
dca61a42-c891-40a0-86ed-a15e8de86024	Grande Prairie	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:grande_prairie	AB	\N	2025-08-01 15:49:44.178541	2025-08-01 15:49:44.178541
0660fb62-df4b-4997-89c7-899bab942bad	Kirkland	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:kirkland	QC	\N	2025-08-01 15:49:44.178543	2025-08-01 15:49:44.178543
050771e2-29b8-43af-92d0-af65a695c18d	Lethbridge	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:lethbridge	AB	\N	2025-08-01 15:49:44.178545	2025-08-01 15:49:44.178546
1b751335-dd9c-498a-bc9a-b4d4b06d5c1b	Edmonton	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:edmonton	AB	\N	2025-08-01 15:49:44.178548	2025-08-01 15:49:44.178548
e83817ff-435d-4d54-89e6-bf9e872e345f	Saint Jean Sur Richelieu	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:saint_jean_sur_richelieu	QC	\N	2025-08-01 15:49:44.178551	2025-08-01 15:49:44.178552
263a1ab8-0d75-4e67-aead-9f73ee96b885	Mississauga	MUNICIPAL	ocd-division/country:ca/province:on/municipality:mississauga	ON	\N	2025-08-01 15:49:44.178554	2025-08-01 15:49:44.178555
bbac90e1-60de-4f7e-bc12-0edd7d247d97	Lincoln	MUNICIPAL	ocd-division/country:ca/province:on/municipality:lincoln	ON	\N	2025-08-01 15:49:44.178557	2025-08-01 15:49:44.178557
e3634b25-5109-4360-95bd-04576733d2bb	Kingston	MUNICIPAL	ocd-division/country:ca/province:on/municipality:kingston	ON	\N	2025-08-01 15:49:44.17856	2025-08-01 15:49:44.17856
93b9f3c2-9b66-4860-8a8a-78527da714e4	Calgary	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:calgary	AB	\N	2025-08-01 15:49:44.178563	2025-08-01 15:49:44.178563
9d7bced2-3e44-4373-98e6-cd6f958e4b97	Milton	MUNICIPAL	ocd-division/country:ca/province:on/municipality:milton	ON	\N	2025-08-01 15:49:44.178566	2025-08-01 15:49:44.178566
39f12654-3270-4233-929b-27df226def2b	Sault Ste Marie	MUNICIPAL	ocd-division/country:ca/province:on/municipality:sault_ste_marie	ON	\N	2025-08-01 15:49:44.178569	2025-08-01 15:49:44.17857
6db8ad90-f48e-4d40-90ec-fafedde43ab0	Cape Breton	MUNICIPAL	ocd-division/country:ca/province:ns/municipality:cape_breton	NS	\N	2025-08-01 15:49:44.178572	2025-08-01 15:49:44.178573
b322e803-2065-4291-b7e9-1f35ba3c18c4	Wood Buffalo	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:wood_buffalo	AB	\N	2025-08-01 15:49:44.178575	2025-08-01 15:49:44.178576
ffa8571d-875e-4ba8-8522-b755e3c8847f	Pointe Claire	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:pointe_claire	QC	\N	2025-08-01 15:49:44.178578	2025-08-01 15:49:44.178579
fca4b237-52f3-4064-8183-0a7b46eb6d7e	Georgina	MUNICIPAL	ocd-division/country:ca/province:on/municipality:georgina	ON	\N	2025-08-01 15:49:44.178582	2025-08-01 15:49:44.178582
b053fad1-d046-4ed7-9f1a-0a71837d9952	Saskatoon	MUNICIPAL	ocd-division/country:ca/province:sk/municipality:saskatoon	SK	\N	2025-08-01 15:49:44.178584	2025-08-01 15:49:44.178585
9ebeec29-aa76-42d7-ac66-aa27c2f8c92b	Vancouver	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:vancouver	BC	\N	2025-08-01 15:49:44.178587	2025-08-01 15:49:44.178587
91748c7e-09dd-4a74-a7ca-2fc170c0bd20	Greater Sudbury	MUNICIPAL	ocd-division/country:ca/province:on/municipality:greater_sudbury	ON	\N	2025-08-01 15:49:44.178591	2025-08-01 15:49:44.178591
30e38784-f276-4476-a069-896f2f83c442	Whitby	MUNICIPAL	ocd-division/country:ca/province:on/municipality:whitby	ON	\N	2025-08-01 15:49:44.178594	2025-08-01 15:49:44.178594
8c4c2b2e-1f8e-4a43-9798-7532ea34f382	Abbotsford	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:abbotsford	BC	\N	2025-08-01 15:49:44.178596	2025-08-01 15:49:44.178597
3d77f970-4529-4f60-bb34-675e82365ebf	Saint Jerome	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:saint_jerome	QC	\N	2025-08-01 15:49:44.178599	2025-08-01 15:49:44.178599
b503c728-2833-4d11-b977-1b5b74dd1de1	Charlottetown	MUNICIPAL	ocd-division/country:ca/province:pe/municipality:charlottetown	PE	\N	2025-08-01 15:49:44.178601	2025-08-01 15:49:44.178602
57fb1ad3-d873-49d2-9cea-8755297037e1	Richmond Hill	MUNICIPAL	ocd-division/country:ca/province:on/municipality:richmond_hill	ON	\N	2025-08-01 15:49:44.178604	2025-08-01 15:49:44.178604
f8042fa6-c447-41d3-a903-c37844e470b1	Regina	MUNICIPAL	ocd-division/country:ca/province:sk/municipality:regina	SK	\N	2025-08-01 15:49:44.178606	2025-08-01 15:49:44.178607
01337e59-b064-4c55-a9ef-12582ca00a9d	Thunder Bay	MUNICIPAL	ocd-division/country:ca/province:on/municipality:thunder_bay	ON	\N	2025-08-01 15:49:44.178609	2025-08-01 15:49:44.178609
88dc287f-47c2-43bc-bf4d-b82415280457	Senneville	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:senneville	QC	\N	2025-08-01 15:49:44.178611	2025-08-01 15:49:44.178612
5902f604-888f-42c0-a9f0-0897fac1bd6d	Lasalle	MUNICIPAL	ocd-division/country:ca/province:on/municipality:lasalle	ON	\N	2025-08-01 15:49:44.178614	2025-08-01 15:49:44.178614
c1ecbeb9-fc63-48a9-9afa-016d97e75453	Wellesley	MUNICIPAL	ocd-division/country:ca/province:on/municipality:wellesley	ON	\N	2025-08-01 15:49:44.178617	2025-08-01 15:49:44.178617
0b9a2412-badc-4374-b855-9a3b53bc25c2	Trois Rivieres	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:trois_rivieres	QC	\N	2025-08-01 15:49:44.17862	2025-08-01 15:49:44.17862
149c538e-a222-4e14-8293-50af2ac6af72	Strathcona County	MUNICIPAL	ocd-division/country:ca/province:ab/municipality:strathcona_county	AB	\N	2025-08-01 15:49:44.178623	2025-08-01 15:49:44.178624
a6289519-2d0c-4e79-a790-6325c6dc6827	Burlington	MUNICIPAL	ocd-division/country:ca/province:on/municipality:burlington	ON	\N	2025-08-01 15:49:44.178626	2025-08-01 15:49:44.178627
3d055818-ca86-4392-a1ae-070f4d3a2b81	Montreal	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:montreal	QC	\N	2025-08-01 15:49:44.178629	2025-08-01 15:49:44.17863
093aa623-5375-49a4-9487-899a2101f7d2	Mercier	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:mercier	QC	\N	2025-08-01 15:49:44.178633	2025-08-01 15:49:44.178633
96bd5410-3697-4386-adba-5d0a57739ff0	Langley	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:langley	BC	\N	2025-08-01 15:49:44.178636	2025-08-01 15:49:44.178636
8040531d-0a45-4b24-98fc-f8073f046623	Summerside	MUNICIPAL	ocd-division/country:ca/province:pe/municipality:summerside	PE	\N	2025-08-01 15:49:44.178639	2025-08-01 15:49:44.17864
d82fcb9e-c574-4bf5-b1ac-eaed0ed0e101	Welland	MUNICIPAL	ocd-division/country:ca/province:on/municipality:welland	ON	\N	2025-08-01 15:49:44.178642	2025-08-01 15:49:44.178643
d028bcb9-cc2b-4964-94c0-eb1b35c7b5b3	Saanich	MUNICIPAL	ocd-division/country:ca/province:bc/municipality:saanich	BC	\N	2025-08-01 15:49:44.178646	2025-08-01 15:49:44.178646
1d8d4560-8ce7-4da4-8d45-a5e4389ab8d8	Woolwich	MUNICIPAL	ocd-division/country:ca/province:on/municipality:woolwich	ON	\N	2025-08-01 15:49:44.178649	2025-08-01 15:49:44.178649
6e7af4e8-666e-41a8-ba71-cc946fb16714	Markham	MUNICIPAL	ocd-division/country:ca/province:on/municipality:markham	ON	\N	2025-08-01 15:49:44.178652	2025-08-01 15:49:44.178652
50622396-9154-4f24-9355-d68531c869a4	Uxbridge	MUNICIPAL	ocd-division/country:ca/province:on/municipality:uxbridge	ON	\N	2025-08-01 15:49:44.178655	2025-08-01 15:49:44.178655
e562d391-413a-4f4e-9c5d-c7e17a3f7a8b	North Dumfries	MUNICIPAL	ocd-division/country:ca/province:on/municipality:north_dumfries	ON	\N	2025-08-01 15:49:44.178658	2025-08-01 15:49:44.178658
1a658218-b740-448f-9365-b7536a775a0d	Montreal Est	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:montreal_est	QC	\N	2025-08-01 15:49:44.178661	2025-08-01 15:49:44.178662
5b31ae80-0e81-47c1-be5d-343abcd30c76	Dorval	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:dorval	QC	\N	2025-08-01 15:49:44.178664	2025-08-01 15:49:44.178665
064d8ca2-30fe-42c8-bc4d-deba5cab43bc	Chatham Kent	MUNICIPAL	ocd-division/country:ca/province:on/municipality:chatham_kent	ON	\N	2025-08-01 15:49:44.178667	2025-08-01 15:49:44.178668
3ce1df52-e3fd-4101-ae9c-edef4c8079a0	Oshawa	MUNICIPAL	ocd-division/country:ca/province:on/municipality:oshawa	ON	\N	2025-08-01 15:49:44.17867	2025-08-01 15:49:44.178671
6ff5068d-99a1-4ba0-892f-2961e29aa3d5	Ottawa	MUNICIPAL	ocd-division/country:ca/province:on/municipality:ottawa	ON	\N	2025-08-01 15:49:44.178674	2025-08-01 15:49:44.178674
7439b026-928b-462f-a04e-df030834d4b8	Gatineau	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:gatineau	QC	\N	2025-08-01 15:49:44.178677	2025-08-01 15:49:44.178677
3cdbe2b7-b343-4424-b793-9a45b3c98d55	Beaconsfield	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:beaconsfield	QC	\N	2025-08-01 15:49:44.17868	2025-08-01 15:49:44.17868
d319bf1c-0adc-43a1-902f-af9eaece9d48	Grimsby	MUNICIPAL	ocd-division/country:ca/province:on/municipality:grimsby	ON	\N	2025-08-01 15:49:44.178683	2025-08-01 15:49:44.178684
dfc0fd14-5242-4669-ba90-5263a35e0e2d	Quebec	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:quebec	QC	\N	2025-08-01 15:49:44.178686	2025-08-01 15:49:44.178687
1b80e043-1193-4da3-80c6-2c12175691e3	Brantford	MUNICIPAL	ocd-division/country:ca/province:on/municipality:brantford	ON	\N	2025-08-01 15:49:44.178689	2025-08-01 15:49:44.178689
fcd23ae9-9485-4a91-8115-4ee42ddd5f13	Wilmot	MUNICIPAL	ocd-division/country:ca/province:on/municipality:wilmot	ON	\N	2025-08-01 15:49:44.178691	2025-08-01 15:49:44.178692
63e61b98-e63c-4dfb-9cdb-506946d0a8d7	Cote Saint Luc	MUNICIPAL	ocd-division/country:ca/province:qc/municipality:cote_saint_luc	QC	\N	2025-08-01 15:49:44.178694	2025-08-01 15:49:44.178695
e2367fa6-6ceb-4558-bd29-1c40662a21ee	St John S	MUNICIPAL	ocd-division/country:ca/province:nl/municipality:st_john_s	NL	\N	2025-08-01 15:49:44.178697	2025-08-01 15:49:44.178697
\.


--
-- Data for Name: representatives; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.representatives (id, jurisdiction_id, name, first_name, last_name, role, party, district, email, phone, office_address, website, facebook_url, twitter_url, instagram_url, linkedin_url, term_start, term_end, photo_url, biography, source_url, external_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scraping_runs; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.scraping_runs (id, jurisdiction_id, run_type, status, start_time, end_time, records_processed, records_created, records_updated, errors_count, error_log, summary, created_at) FROM stdin;
\.


--
-- Data for Name: votes; Type: TABLE DATA; Schema: public; Owner: ashishtandon
--

COPY public.votes (id, event_id, bill_id, representative_id, vote_result, vote_date, source_url, created_at) FROM stdin;
\.


--
-- Name: data_collection_tracking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openpolicy
--

SELECT pg_catalog.setval('public.data_collection_tracking_id_seq', 1, false);


--
-- Name: bill_sponsorships bill_sponsorships_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bill_sponsorships
    ADD CONSTRAINT bill_sponsorships_pkey PRIMARY KEY (id);


--
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (id);


--
-- Name: committee_memberships committee_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committee_memberships
    ADD CONSTRAINT committee_memberships_pkey PRIMARY KEY (id);


--
-- Name: committees committees_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT committees_pkey PRIMARY KEY (id);


--
-- Name: data_collection_tracking data_collection_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: openpolicy
--

ALTER TABLE ONLY public.data_collection_tracking
    ADD CONSTRAINT data_collection_tracking_pkey PRIMARY KEY (id);


--
-- Name: data_quality_issues data_quality_issues_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.data_quality_issues
    ADD CONSTRAINT data_quality_issues_pkey PRIMARY KEY (id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: jurisdictions jurisdictions_division_id_key; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.jurisdictions
    ADD CONSTRAINT jurisdictions_division_id_key UNIQUE (division_id);


--
-- Name: jurisdictions jurisdictions_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.jurisdictions
    ADD CONSTRAINT jurisdictions_pkey PRIMARY KEY (id);


--
-- Name: representatives representatives_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.representatives
    ADD CONSTRAINT representatives_pkey PRIMARY KEY (id);


--
-- Name: scraping_runs scraping_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.scraping_runs
    ADD CONSTRAINT scraping_runs_pkey PRIMARY KEY (id);


--
-- Name: bills uq_bill_number; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT uq_bill_number UNIQUE (jurisdiction_id, bill_number);


--
-- Name: bill_sponsorships uq_bill_sponsorship; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bill_sponsorships
    ADD CONSTRAINT uq_bill_sponsorship UNIQUE (bill_id, representative_id);


--
-- Name: committees uq_committee_name; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT uq_committee_name UNIQUE (jurisdiction_id, name);


--
-- Name: votes uq_event_representative_vote; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT uq_event_representative_vote UNIQUE (event_id, representative_id);


--
-- Name: representatives uq_representative_external_id; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.representatives
    ADD CONSTRAINT uq_representative_external_id UNIQUE (jurisdiction_id, external_id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (id);


--
-- Name: idx_bill_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_bill_jurisdiction ON public.bills USING btree (jurisdiction_id);


--
-- Name: idx_bill_number; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_bill_number ON public.bills USING btree (bill_number);


--
-- Name: idx_bill_sponsorship_bill; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_bill_sponsorship_bill ON public.bill_sponsorships USING btree (bill_id);


--
-- Name: idx_bill_sponsorship_representative; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_bill_sponsorship_representative ON public.bill_sponsorships USING btree (representative_id);


--
-- Name: idx_bill_status; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_bill_status ON public.bills USING btree (status);


--
-- Name: idx_committee_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_committee_jurisdiction ON public.committees USING btree (jurisdiction_id);


--
-- Name: idx_committee_membership_committee; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_committee_membership_committee ON public.committee_memberships USING btree (committee_id);


--
-- Name: idx_committee_membership_representative; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_committee_membership_representative ON public.committee_memberships USING btree (representative_id);


--
-- Name: idx_data_quality_detected; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_data_quality_detected ON public.data_quality_issues USING btree (detected_at);


--
-- Name: idx_data_quality_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_data_quality_jurisdiction ON public.data_quality_issues USING btree (jurisdiction_id);


--
-- Name: idx_data_quality_severity; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_data_quality_severity ON public.data_quality_issues USING btree (severity);


--
-- Name: idx_data_quality_type; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_data_quality_type ON public.data_quality_issues USING btree (issue_type);


--
-- Name: idx_event_date; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_event_date ON public.events USING btree (event_date);


--
-- Name: idx_event_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_event_jurisdiction ON public.events USING btree (jurisdiction_id);


--
-- Name: idx_event_type; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_event_type ON public.events USING btree (event_type);


--
-- Name: idx_jurisdiction_province; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_jurisdiction_province ON public.jurisdictions USING btree (province);


--
-- Name: idx_jurisdiction_type; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_jurisdiction_type ON public.jurisdictions USING btree (jurisdiction_type);


--
-- Name: idx_representative_district; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_representative_district ON public.representatives USING btree (district);


--
-- Name: idx_representative_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_representative_jurisdiction ON public.representatives USING btree (jurisdiction_id);


--
-- Name: idx_representative_party; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_representative_party ON public.representatives USING btree (party);


--
-- Name: idx_representative_role; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_representative_role ON public.representatives USING btree (role);


--
-- Name: idx_scraping_run_jurisdiction; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_scraping_run_jurisdiction ON public.scraping_runs USING btree (jurisdiction_id);


--
-- Name: idx_scraping_run_start_time; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_scraping_run_start_time ON public.scraping_runs USING btree (start_time);


--
-- Name: idx_scraping_run_status; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_scraping_run_status ON public.scraping_runs USING btree (status);


--
-- Name: idx_vote_bill; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_vote_bill ON public.votes USING btree (bill_id);


--
-- Name: idx_vote_date; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_vote_date ON public.votes USING btree (vote_date);


--
-- Name: idx_vote_event; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_vote_event ON public.votes USING btree (event_id);


--
-- Name: idx_vote_representative; Type: INDEX; Schema: public; Owner: ashishtandon
--

CREATE INDEX idx_vote_representative ON public.votes USING btree (representative_id);


--
-- Name: bill_sponsorships bill_sponsorships_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bill_sponsorships
    ADD CONSTRAINT bill_sponsorships_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES public.bills(id);


--
-- Name: bill_sponsorships bill_sponsorships_representative_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bill_sponsorships
    ADD CONSTRAINT bill_sponsorships_representative_id_fkey FOREIGN KEY (representative_id) REFERENCES public.representatives(id);


--
-- Name: bills bills_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: committee_memberships committee_memberships_committee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committee_memberships
    ADD CONSTRAINT committee_memberships_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES public.committees(id);


--
-- Name: committee_memberships committee_memberships_representative_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committee_memberships
    ADD CONSTRAINT committee_memberships_representative_id_fkey FOREIGN KEY (representative_id) REFERENCES public.representatives(id);


--
-- Name: committees committees_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.committees
    ADD CONSTRAINT committees_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: data_quality_issues data_quality_issues_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.data_quality_issues
    ADD CONSTRAINT data_quality_issues_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: events events_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES public.bills(id);


--
-- Name: events events_committee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES public.committees(id);


--
-- Name: events events_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: representatives representatives_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.representatives
    ADD CONSTRAINT representatives_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: scraping_runs scraping_runs_jurisdiction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.scraping_runs
    ADD CONSTRAINT scraping_runs_jurisdiction_id_fkey FOREIGN KEY (jurisdiction_id) REFERENCES public.jurisdictions(id);


--
-- Name: votes votes_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES public.bills(id);


--
-- Name: votes votes_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: votes votes_representative_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ashishtandon
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_representative_id_fkey FOREIGN KEY (representative_id) REFERENCES public.representatives(id);


--
-- PostgreSQL database dump complete
--

