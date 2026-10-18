--sqlite3 "Bite Size/database/cases.db"
--SELECT * FROM cases;        SHOWS EVERYTHING IN CASES DB
--SELECT * FROM saved_case_folders;
--SELECT * FROM saved_cases;
--SELECT name FROM cases;     SHOWS 'name' element of each element in table
--.schema cases               SHOWS ELEMENT LAYOUT FOR TABLE
--SELECT * FROM cases WHERE name = 'CASE NAME';  FINDS WHERE AN ELEMENT IS EQUAL TO 'given value'

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    year TEXT,
    court TEXT,
    facts TEXT,
    plaintiff_argument TEXT,
    defendant_argument TEXT,
    ruling TEXT,
    opinion TEXT,
    significance TEXT
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Brown v. Board of Education',
    '1954',
    'United States Supreme Court',
    'African American students were denied equal access to public schools because of segregation laws. The case challenged the constitutionality of segregated public education.',
    'The plaintiffs argued that segregation in public schools violated the Equal Protection Clause and harmed children psychologically and educationally.',
    'The defendants argued that education could be separate if it was equal and that states had authority to manage school systems.',
    'The Court held that segregated public schools were unconstitutional because they denied equal protection under the law.',
    'The Court explained that separate educational facilities are inherently unequal and therefore violate the Constitution.',
    'The decision dismantled legal segregation in public education and became a cornerstone of the civil rights movement.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Dred Scott v. Sandford',
    '1857',
    'United States Supreme Court',
    'Dred Scott, an enslaved African American man, was taken by his owners from the slave state of Missouri into Illinois and the Wisconsin Territory, where slavery was illegal under federal law. After returning to Missouri, Scott sued for his freedom, arguing that his residence in free territory made him a free man.',
    'Scott argued that because he had resided in a free state and a free territory, his status as an enslaved person was permanently dissolved, making him a free citizen entitled to sue in federal court.',
    'John Sanford argued that Scott was a person of African descent and born into slavery, meaning he was not a citizen of the United States or the state of Missouri, and therefore lacked the legal standing to bring a lawsuit in federal court.',
    'The Supreme Court ruled that African Americans, whether enslaved or free, were not citizens of the United States and could not sue in federal court, and that the Missouri Compromise was unconstitutional.',
    'Chief Justice Roger Taney argued that people of African descent were not included in the Constitution''s definition of citizens and that Congress could not prohibit slavery in U.S. territories.',
    'Widely considered the worst decision in Supreme Court history, this ruling de facto nationalized slavery, deeply polarized the nation, and served as a major catalyst that accelerated the outbreak of the American Civil War.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Gideon v. Wainwright',
    '1963',
    'United States Supreme Court',
    'Clarence Earl Gideon was charged in Florida for breaking and entering with the intent to commit petty larceny. He requested a lawyer but was denied because Florida only provided counsel in capital cases. Gideon represented himself at trial and was convicted.',
    'Gideon argued that the Sixth Amendment guaranteed him the right to counsel in criminal prosecutions, and that the Fourteenth Amendment applied that right to the states.',
    'The State of Florida argued that the Constitution did not require the state to provide counsel in non-capital felony cases and that Gideon had been afforded due process.',
    'The Supreme Court ruled that the Sixth Amendment right to counsel is fundamental and must be provided to criminal defendants in state courts as well.',
    'Justice Black wrote that the right to counsel is necessary to ensure a fair trial and that the state cannot deprive a defendant of a fair defense because of poverty.',
    'This case extended the right to counsel to state criminal defendants and transformed indigent defense across the United States.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Marbury v. Madison',
    '1803',
    'United States Supreme Court',
    'William Marbury was appointed a justice of the peace in the final hours of John Adams''s presidency, but his commission was not delivered before Thomas Jefferson took office. Marbury sued to compel Madison to deliver the commission.',
    'Marbury argued that the law entitled him to his commission and that the judiciary had authority to enforce that right.',
    'Madison argued that the Court could not compel the delivery of the commission because the law giving Marbury the right to sue was unconstitutional.',
    'The Supreme Court ruled that Marbury had a right to the commission, but the Court could not issue the writ because the statute that gave it jurisdiction was unconstitutional.',
    'Chief Justice Marshall held that the Constitution is supreme and that it is the duty of the judiciary to say what the law is. This established judicial review.',
    'This case created the power of judicial review, allowing courts to strike down laws that conflict with the Constitution.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'McCulloch v. Maryland',
    '1819',
    'United States Supreme Court',
    'The federal government created the Second Bank of the United States. Maryland tried to tax the bank''s Baltimore branch, and McCulloch, the cashier, refused to pay the tax.',
    'McCulloch argued that the federal government had authority to create a bank and that Maryland could not tax a federal institution.',
    'Maryland argued that states retained the power to tax businesses operating within their borders and that the federal bank was not constitutionally authorized.',
    'The Court ruled that Congress had implied powers under the Necessary and Proper Clause and that states could not tax the federal government.',
    'Chief Justice Marshall explained that the Constitution grants powers beyond the enumerated list when those powers are necessary to carry out federal responsibilities.',
    'This case strengthened federal power and clarified that states cannot interfere with valid federal actions.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Miranda v. Arizona',
    '1966',
    'United States Supreme Court',
    'Ernesto Miranda was arrested by Phoenix police and interrogated for two hours regarding a kidnapping and rape. He signed a written confession during the interrogation, but police had never informed him of his right to remain silent or his right to have an attorney present.',
    'Miranda argued that his confession was obtained unconstitutionally because police failed to inform him of his rights, violating his Fifth Amendment protection against self-incrimination and his Sixth Amendment right to counsel.',
    'The State of Arizona argued that Miranda''s confession was given voluntarily, that he was aware of his legal rights despite not being explicitly read them, and that the police followed proper procedures for a custodial interrogation.',
    'The Supreme Court ruled that prosecutors cannot use statements from custodial interrogation unless they demonstrate the use of procedural safeguards effective to secure the privilege against self-incrimination.',
    'Chief Justice Earl Warren held that the modern practice of in-custody interrogation is psychologically oriented and inherently coercive. Therefore, suspects must be informed prior to questioning that they have the right to remain silent, that anything they say can be used against them, and that they have the right to an attorney.',
    'This case mandated the creation of the universal ''Miranda Warning'' (''You have the right to remain silent...''), completely altering American police procedures to protect suspects'' constitutional rights during arrests.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Obergefell v. Hodges',
    '2015',
    'United States Supreme Court',
    'Same-sex couples challenged state bans on marriage recognition.',
    'Marriage recognition is a constitutional right.',
    'States can define marriage as they choose.',
    'The Court held that same-sex couples have a constitutional right to marry.',
    'Justice Kennedy wrote that the right to marry is fundamental.',
    'It legalized same-sex marriage nationally.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Plessy v. Ferguson',
    '1896',
    'United States Supreme Court',
    'Homer Plessy, an African American man who was seven-eighths Caucasian, was arrested for refusing to leave a "Whites-only" railcar in Louisiana, deliberately challenging the state''s Separate Car Act.',
    'The segregation law violated the 14th Amendment’s Equal Protection Clause and the 13th Amendment by treating Black citizens as legally inferior.',
    'Louisiana had the police power to regulate social order, and separating the races did not imply inferiority as long as facilities were equal.',
    '7–1 decision against Plessy, upholding the Louisiana segregation law as constitutional.',
    'Written by Justice Henry Billings Brown, stating that the 14th Amendment enforced political equality, not social mixing. Justice John Marshall Harlan dissented, famously writing that "Our Constitution is color-blind."',
    'Established the devastating "separate but equal" doctrine, legalizing Jim Crow segregation across the American South until it was overturned by Brown v. Board of Education in 1954.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Template Case Information',
    '2026',
    'Example Court',
    'Example facts.',
    'Example plaintiff.',
    'Example defendant.',
    'Example ruling.',
    'Example opinion.',
    'Example significance.'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'United States v. Lopez',
    '1995',
    'United States Supreme Couhrt',
    'High school student Alfonso Lopez brought a concealed handgun to school in Texas and was charged under the federal Gun-Free School Zones Act of 1990.',
    'The United States argued that gun violence in schools hurts the economy by disrupting education and travel, giving Congress the authority to ban guns near schools under its power to regulate commerce.',
    'Lopez argued that the Gun-Free School Zones Act was unconstitutional because public education and gun laws are local matters reserved to the states, not interstate commerce.',
    '5–4 decision against the United States.',
    'Written by Chief Justice William Rehnquist, ruling that the possession of a gun in a local school zone is a non-economic activity that does not significantly affect interstate commerce, meaning Congress exceeded its authority.',
    'Marked a major shift in modern constitutional history by limiting the scope of Congress''s Commerce Clause power and protecting state sovereignty (devolution).'
);

INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Schenck v. United States',
    '1919',
    'United States Supreme Court',
    'During World War I, socialist activists were arrested and convicted under the Espionage Act for distributing leaflets that urged draftees to peacefully resist military conscription.',
    'Schenck argued that the leaflets were protected under the First Amendment freedom of speech and expression.',
    'The United States government argued that speech aimed at disrupting the military draft during wartime directly threatens national security.',
    'The Court held that the conviction was constitutional and that free speech protections can be limited during times of war.',
    'Justice Holmes wrote that speech is not protected if the words used create a clear and present danger to national safety.',
    'It established the clear and present danger test, setting a baseline standard for when the government can limit political speech.'
);


INSERT INTO cases (
    name, year, court, facts, plaintiff_argument,
    defendant_argument, ruling, opinion, significance
) VALUES (
    'Baker v. Carr', '1962', 'United States Supreme Court',
    'Tennessee failed to reapportion its General Assembly since 1901, causing severe malapportionment favoring rural voters over urban residents.',
    'Urban voters argued malapportionment denied equal protection under the law.',
    'Tennessee argued redistricting was a non-justiciable political question.',
    'The Court held apportionment claims are justiciable under the Equal Protection Clause.',
    'Justice Brennan noted malapportionment claims do not present a political question.',
    'Established the "one person, one vote" principle.'
);

CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    leading_agency TEXT,
    key_dates TEXT,
    summary_of_facts TEXT,
    issue TEXT
);

INSERT INTO bills (
    name,
    leading_agency,
    key_dates,
    summary_of_facts,
    issue
) VALUES (
    'SAFE Drugs Act',
    'Senate Health Committee',
    '2026 introduction, 2027 hearing',
    'The bill would expand access to treatment and tighten oversight for prescription medication safety.',
    'The legislation addresses dangerous drug shortages and the approval process for prescription medications.'
);

INSERT INTO bills (
    name,
    leading_agency,
    key_dates,
    summary_of_facts,
    issue
) VALUES (
    'Protect College Sports Act',
    'Senate Commerce Committee',
    'May 2026 introduced, September 2026 passed Senate',
    'The bill standardizes college athletics by codifying student-athlete revenue sharing, creating a uniform federal NIL framework that overrides state laws, capping agent fees at 5%, guaranteeing 10-year scholarships, and extending post-eligibility medical coverage.',
    'The legislation addresses the legal instabilities facing the NCAA due to antitrust challenges, the uncoordinated patchwork of state NIL laws, and the erosion of traditional amateurism frameworks.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Website Save Test Case',
    '2026',
    'State Court',
    'Facts',
    'Argument',
    'Defense',
    'Ruling',
    'Opinion',
    'Significance'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Engel v. Vitale',
    '1962',
    'United States Supreme Court',
    'The New York Board of Regents authorized a short, voluntary prayer for recitation at the start of the school day to encourage good citizenship.',
    'Parents of students argued that a state-sponsored prayer in public schools violated the Establishment Clause of the First Amendment.',
    'The school board argued the prayer was voluntary, non-denominational, and did not establish an official state religion.',
    'The Court ruled 6-1 that state-sponsored prayer in public schools is unconstitutional.',
    'Justice Black wrote that the constitutional prohibition against laws establishing religion means the government has no business drafting official prayers for Americans to recite.',
    'Established that public schools cannot sponsor religious activities, strengthening the wall of separation between church and state.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Tinker v. Des Moines Independent Community School District',
    '1969',
    'United States Supreme Court',
    'A group of students wore black armbands to school to protest the Vietnam War and were suspended after refusing to remove them.',
    'The students argued that the armbands were a form of protected symbolic speech under the First Amendment and did not disrupt learning.',
    'The school district argued that the ban was necessary to maintain discipline and prevent potential school disruptions.',
    'The Court ruled 7-2 that students do not lose their First Amendment rights to freedom of speech when they step onto school property.',
    'Justice Fortas wrote that to justify suppressing speech, school officials must prove the conduct would "materially and substantially interfere" with the operation of the school.',
    'Protected students'' symbolic speech rights in public schools, drawing a line between speech and disruptive conduct.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'New York Times Co. v. United States',
    '1971',
    'United States Supreme Court',
    'The Nixon administration attempted to prevent the New York Times and Washington Post from publishing the classified "Pentagon Papers," which detailed the history of U.S. involvement in Vietnam.',
    'The newspapers argued that the government''s attempt to halt publication was an unconstitutional prior restraint that violated freedom of the press.',
    'The government argued that the publication of top-secret documents posed a threat to national security and executive authority.',
    'The Court ruled 6-3 that the government did not meet the heavy burden required to justify prior restraint.',
    'The per curiam opinion stated that any system of prior restraints comes to the Court bearing a heavy presumption against its constitutional validity.',
    'Bolstered freedom of the press by firmly limiting the government''s ability to use "national security" to censor the media prior to publication.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Wisconsin v. Yoder',
    '1972',
    'United States Supreme Court',
    'Three Amish parents refused to send their children to public schools after the eighth grade, violating a Wisconsin law requiring school attendance until age 16.',
    'The parents argued that compulsory high school attendance conflicted with the fundamental tenets of their religious beliefs and lifestyle.',
    'Wisconsin argued that the state had a compelling interest in mandatory education to prepare citizens to participate productively in society.',
    'The Court ruled unanimously (7-0) that the state''s interest in compulsory education was outweighed by the religious freedom of the Amish.',
    'Chief Justice Burger noted that an additional one or two years of formal high school would not produce the benefits the state cited and would severely burden Amish religious practices.',
    'Affirmed that the Free Exercise Clause protects religious practices against state laws, unless the state can show a compelling interest using the least restrictive means.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Roe v. Wade',
    '1973',
    'United States Supreme Court',
    'A Texas resident challenged a state law making abortion illegal except by doctor''s orders to save a woman''s life.',
    'The plaintiff argued that the Texas statutes unconstitutionally invaded her right to personal privacy protected by the First, Fourth, Fifth, Ninth, and Fourteenth Amendments.',
    'Texas argued that it had a compelling interest in protecting the life of the unborn fetus from the moment of conception.',
    'The Court ruled 7-2 that a woman''s right to an abortion fell within the right to privacy protected by the Fourteenth Amendment.',
    'Justice Blackmun established a trimester framework, ruling that the state cannot restrict abortion in the first trimester, but can implement increasing regulations in the second and third trimesters.',
    'Legalized abortion nationwide by linking it to a constitutional right to privacy (overturned in 2022 by Dobbs v. Jackson.)'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Shaw v. Reno',
    '1993',
    'United States Supreme Court',
    'North Carolina created a highly unusually shaped, 160-mile-long majority-black legislative district to comply with the Voting Rights Act of 1965.',
    'White voters argued that the district''s bizarre shape was drawn solely along racial lines, violating the Equal Protection Clause.',
    'The state argued that the district was constitutional because its purpose was to comply with federal law and increase minority representation.',
    'The Court ruled 5-4 that a district drawn to be so bizarre that it separates voters based on race must face strict scrutiny.',
    'Justice O''Connor wrote that the district''s shape bore an uncomfortable resemblance to political apartheid and sent a message that elected officials should represent only one racial group.',
    'Established that while race can be considered in redistricting, race-conscious gerrymandering must satisfy strict scrutiny and cannot be the sole factor in drawing bizarrely shaped districts.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'McDonald v. Chicago',
    '2010',
    'United States Supreme Court',
    'Following a previous SCOTUS ruling striking down a federal handgun ban (District of Columbia v. Heller), residents challenged a strict handgun ban enacted by the city of Chicago.',
    'Residents argued that the Second Amendment right to keep and bear arms applies to state and local governments, not just the federal government.',
    'Chicago argued that states and cities have police powers to regulate or ban handguns to maintain public safety and reduce crime.',
    'The Court ruled 5-4 that the Fourteenth Amendment makes the Second Amendment right to keep and bear arms for self-defense applicable to the states.',
    'Justice Alito wrote that the right to self-defense is deeply rooted in the nation''s history and tradition, making it a fundamental right.',
    'Incorporated the Second Amendment right to bear arms to state and local governments via the Due Process Clause of the Fourteenth Amendment.'
);

INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    'Citizens United v. Federal Election Commission',
    '2010',
    'United States Supreme Court',
    'A conservative non-profit organization produced a critical film about Hillary Clinton and wanted to advertise and broadcast it, but was blocked by the Bipartisan Campaign Reform Act (BCRA), which restricted corporate funding of political broadcasts.',
    'Citizens United argued that the restrictions on corporate funding of independent political broadcasts violated the First Amendment freedom of speech.',
    'The FEC argued that limits on corporate spending were necessary to prevent political corruption and maintain public confidence in elections.',
    'The Court ruled 5-4 that corporate funding of independent political broadcasts in candidate elections cannot be limited.',
    'Justice Kennedy wrote that the First Amendment protects political speech, and the government cannot suppress political speech simply because the speaker is a corporation.',
    'Ruled that corporations and unions have First Amendment speech rights, leading to the creation of Super PACs and a massive increase in independent campaign spending.'
);

COMMIT;
