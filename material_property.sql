show databases;

CREATE DATABASE material_property;

-- 2. Use the newly created database
USE material_property;

-- 3. Create the Material table
CREATE TABLE Material (
    material_code VARCHAR(50) PRIMARY KEY,
    material_description VARCHAR(255),
    Uom VARCHAR(50),
    Plant VARCHAR(50)
);

-- 4. Create the Vendor table
CREATE TABLE Vendor (
    material_code VARCHAR(50),
    vendor_code VARCHAR(20) not null,
    vendor_name VARCHAR(255) not null,
    PRIMARY KEY (material_code, vendor_code),
  FOREIGN KEY (material_code) REFERENCES Material(material_code) ON DELETE CASCADE
  on update cascade
);
drop table vendor;

INSERT INTO MATERIAL(material_code,material_description, Uom, Plant) 
values
("TRAYSIG000023","OPEN-TRAY, 3 * 10, 200 ML-BUTTERMILK-SIG","EA","GM01"
);
INSERT INTO MATERIAL (material_code, material_description, Uom, Plant) 
VALUES
("TRAYSIG000029", "OPEN-TRAY, 3 * 10, 200 ML-ROSE LASSI-SIG", "EA", "GM01"),
("SRNFGEN000013", "SHRINK FILM W:480MM THICKNESS:60+/-5MIC", "KG", "GM01"),
("LSLVSIG000006", "SLEEVE 150 ML - APPLE TRU - SIG", "Pallet", "GM01"),
("LSLVSIG000010", "SLEEVE 150 ML - MANGO TRU - SIG", "Pallet", "GM01"),
("LSLVSIG000014", "SLEEVE 150 ML - ORANGE TRU - SIG", "Pallet", "GM01"),
("LSLVSIG000021", "SLEEVE 200 ML - BUTTERMILK - SIG", "Pallet", "GM01"),
("LSLVSIG000022", "SLEEVE 200 ML SIG - ROSE LASSI", "Pallet", "GM01"),
("LSLVSIG000023", "SLEEVE 250ML SIG COMBISMILE(S)- R.LASSI", "Pallet", "GM01"),
("LSLVSIG000024", "SPOUT 250 ML SIG COMBIGO SMALL", "Pallet", "GM01"),
("TRAYSIG000025", "WA TRAY 250ML SIG COMBISMILE-ROSE LASSI", "EA", "GM01");

select * from material;

INSERT INTO Vendor (material_code, vendor_code, vendor_name)
VALUES
('LSLVSIG000006', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000010', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000014', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000021', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000022', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000023', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('LSLVSIG000024', '1066193', 'SIG Combibloc India Pvt Ltd.'),
('SRNFGEN000013', '1000225', 'AmulFed Dairy Packaging Film Plant'),
('SRNFGEN000013', '1004080', 'Bakulesh Fabricators'),
('SRNFGEN000013', '1004994', 'Aaaka Plastics'),
('SRNFGEN000013', '1012427', 'Swastik Multi Pack'),
('TRAYSIG000023', '1000990', 'Gujarat Print Pack Publications'),
('TRAYSIG000023', '1004911', 'Jay Boxes'),
('TRAYSIG000023', '1040839', 'J M Packaging'),
('TRAYSIG000023', '1057432', 'V S Packaging Indistries'),
('TRAYSIG000025', '1000990', 'Gujarat Print Pack Publications'),
('TRAYSIG000025', '1004911', 'Jay Boxes'),
('TRAYSIG000025', '1040839', 'J M Packaging'),
('TRAYSIG000025', '1057432', 'V S Packaging Indistries'),
('TRAYSIG000029', '1000990', 'Gujarat Print Pack Publications'),
('TRAYSIG000029', '1004911', 'Jay Boxes'),
('TRAYSIG000029', '1040839', 'J M Packaging'),
('TRAYSIG000029', '1057432', 'V S Packaging Indistries');

select* from vendor;
create table employee
(Username int not null primary key,
Password int not null);
insert into employee(Username,Password)
values(12001504,2001),
(12001505,2001);

select* from employee;

CREATE INDEX idx_material_code ON Vendor(material_code);
