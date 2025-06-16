clear;

dx = 0.1;
dz = 1;

px = 8e-3;

dpx_M1 = 198;%%%%
dpx_M2 = 159;%%%%

M1 = dpx_M1/dx*px;
M2 = dpx_M2/dx*px;

disp(M1);
disp(M2);

Z_so = M2*dz/(M1-M2);
Z_sd = M1*Z_so;

disp('Z_so:');
disp(Z_so)
disp('Z_sd:');
disp(Z_sd);

%%

ang_left = -91.26;
ang_right = -88.43;

rot_phi_ang = ((90-abs(ang_left))+(90-abs(ang_right)))/2;
rot_phi = tand(rot_phi_ang);

disp('rot_phi:');
disp(rot_phi);