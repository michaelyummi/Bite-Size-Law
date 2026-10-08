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

COMMIT;
