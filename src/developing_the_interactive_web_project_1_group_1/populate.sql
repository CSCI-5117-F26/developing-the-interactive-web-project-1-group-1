INSERT INTO tag_building (building_name, address, latitude, longitude) VALUES
    /* East Bank */
    ('Akerman Hall', '110 Union St SE, Minneapolis, MN 55455', 44.9753004, -93.2323027),
    ('Amundson Hall', '421 Washington Ave SE, Minneapolis, MN 55455', 44.9739501, -93.2330947),
    ('Bruininks Hall', '222 Pleasant St SE, Minneapolis, MN 55455', 44.9740838, -93.2373302),
    ('Coffman Memorial Union', '300 Washington Ave SE, Minneapolis, MN 55455', 44.9728172, -93.2353517),
    ('Folwell Hall', '9 Pleasant St SE, Minneapolis, MN 55455', 44.9782797, -93.2344904),
    ('Ford Hall', '224 Church St SE, Minneapolis, MN 55455', 44.973899, -93.2344398),
    ('Keller Hall', '200 Union St SE, Minneapolis, MN 55455', 44.9745356, -93.232237),
    ('Lind Hall', '207 Church St SE, Minneapolis, MN 55455', 44.9745174, -93.2335341),
    ('Moos Tower', '515 Delaware St SE, Minneapolis, MN 55455', 44.9729048, -93.2314206),
    ('Northrop', '84 Church St SE, Minneapolis, MN 55455', 44.9764788, -93.2353693),
    ('Recreation and Wellness Center', '123 Harvard St SE, Minneapolis, MN 55455', 44.9756669, -93.2299545),
    ('Smith Hall', '207 Pleasant St SE, Minneapolis, MN 55455', 44.9743706, -93.2362303),
    ('Tate Hall', '116 Church St SE, Minneapolis, MN 55455', 44.9753053, -93.2344511),
    ('Vincent Hall', '206 Church St SE, Minneapolis, MN 55455', 44.9745462, -93.2347364),
    ('Walter Library', '117 Pleasant St SE, Minneapolis, MN 55455', 44.9753648, -93.2362953),
    /* West Bank */
    ('Anderson Hall', '257 19th Ave S, Minneapolis, MN 55455', 44.9720089, -93.242338),
    ('Blegen Hall', '269 19th Ave S, Minneapolis, MN 55455', 44.9718523, -93.2433446),
    ('Carlson School of Management', '321 19th Ave S, Minneapolis, MN 55455', 44.970463, -93.2447716),
    ('Hanson Hall', '1925 S 4th St, Minneapolis, MN 55455', 44.9694546, -93.2446484),
    ('Wilson Library', '309 19th Ave S, Minneapolis, MN 55455', 44.9708194, -93.2435866)
ON CONFLICT (building_name) DO UPDATE
SET address = EXCLUDED.address, latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude;

INSERT INTO tag_itemtype (item_name) VALUES
	('UCard'),
	('Water Bottles & Drinkware'),
	('Bags & Backpacks'),
	('Books & Notes'),
	('Childrens'' Items'),
	('Clothing'),
	('Electronics'),
	('Eyewear'),
	('Footwear'),
	('Keys'),
	('Wallets & Purses'),
	('Watches & Jewelry'),
	('Other')
ON CONFLICT (item_name) DO NOTHING;
