/* ------------------------------------------------------------------------- *
*
*    Copyright (C) 2023 Jake Kurtz
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with this program. If not, see <https://www.gnu.org/licenses/>.
*
* ------------------------------------------------------------------------- */

/* -------------------------------- Textures -------------------------------- */

uniform sampler3D noise_tex_3D_64;
uniform sampler3D noise_tex_3D_128;
uniform sampler2D noise_tex_2D_2048;
uniform sampler2D blue_noise;
uniform sampler2D moon_albedo_tex;
uniform sampler2D moon_normal_tex;
uniform sampler2D irra_tex;
/* -------------------------------------------------------------------------- */
/*                                   UTILITY                                  */
/* -------------------------------------------------------------------------- */

uniform vec2 img_size;

#define M_PI        3.1415926535897932
#define M_3_16PI    0.0596831036594607 // 3 / (16pi)
#define M_1_PI      0.3183098861837906 // 1 / pi
#define M_1_2PI     0.1591549430918953 // 1 / (2pi)
#define M_1_4PI     0.0795774715459476 // 1 / (4pi)
#define M_PI_180    0.0174532925199432 // pi / 180
#define M_2PI       6.2831853071795864 // 2pi

struct Ray
{
    vec3 pos;
    vec3 dir;
};

struct Light
{
    vec3 dir;
    float intsty;
    float silver_intsty;
    float silver_spread;
};

float saturate(float x)
{
    return clamp(x, 0.0, 1.0);
}

float remap(float v, float l1, float h1, float l2, float h2)
{
    return l2 + (v - l1) * (h2 - l2) / (h1 - l1);
}

vec4 tex_sample(sampler2D tex, vec2 uv)
{
    return texture(tex, mod(uv, vec2(1.0)));
}

vec4 bicubic_sample(sampler2D tex, vec2 uv, vec2 size) 
{
    vec2 tex_size = size;
    vec2 inv_tex_size = 1.0 / tex_size;

    vec2 tc = uv * tex_size - 0.5;
    vec2 f = fract(tc);
    tc -= f;
 
    // we'll need the second and third powers
    // of f to compute our filter weights
    vec2 f2 = f * f;
    vec2 f3 = f2 * f;
 
    //compute the filter weights
    vec2 w0 = f2 - 0.5 * (f3 + f);
    vec2 w1 = 1.5 * f3 - 2.5 * f2 + 1.0;
    vec2 w3 = 0.5 * (f3 - f2);
    vec2 w2 = 1.0 - w0 - w1 - w3;

    vec2 s0 = w0 + w1;
    vec2 s1 = w2 + w3;
 
    vec2 f0 = w1 / (w0 + w1);
    vec2 f1 = w3 / (w2 + w3);
 
    vec2 t0 = tc - 1.0 + f0;
    vec2 t1 = tc + 1.0 + f1;

    t0 *= inv_tex_size;
    t1 *= inv_tex_size;

    return
        (texture( tex, vec2( t0.x, t0.y ) ) * s0.x
      +  texture( tex, vec2( t1.x, t0.y ) ) * s1.x) * s0.y
      + (texture( tex, vec2( t0.x, t1.y ) ) * s0.x
      +  texture( tex, vec2( t1.x, t1.y ) ) * s1.x) * s1.y;
}

vec4 bicubic_sample(sampler3D tex, vec3 uvw, vec3 size) 
{
    vec3 tex_size = size;
    vec3 inv_tex_size = 1.0 / tex_size;

    vec3 tc = mod(uvw, vec3(1.0)) * tex_size - 0.5;
    vec3 f = fract(tc);
    tc -= f;
 
    // we'll need the second and third powers
    // of f to compute our filter weights
    vec3 f2 = f * f;
    vec3 f3 = f2 * f;
 
    //compute the filter weights
    vec3 w0 = f2 - 0.5 * (f3 + f);
    vec3 w1 = 1.5 * f3 - 2.5 * f2 + 1.0;
    vec3 w3 = 0.5 * (f3 - f2);
    vec3 w2 = 1.0 - w0 - w1 - w3;

    vec3 s0 = w0 + w1;
    vec3 s1 = w2 + w3;
 
    vec3 f0 = w1 / (w0 + w1);
    vec3 f1 = w3 / (w2 + w3);
 
    vec3 t0 = tc - 1.0 + f0;
    vec3 t1 = tc + 1.0 + f1;

    t0 *= inv_tex_size;
    t1 *= inv_tex_size;

    return
        texture( tex, vec3( t0.x, t0.y, t0.z ) ) * s0.x * s0.y * s0.z
      + texture( tex, vec3( t1.x, t0.y, t0.z ) ) * s1.x * s0.y * s0.z
      + texture( tex, vec3( t0.x, t1.y, t0.z ) ) * s0.x * s1.y * s0.z
      + texture( tex, vec3( t1.x, t1.y, t0.z ) ) * s1.x * s1.y * s0.z
      + texture( tex, vec3( t0.x, t0.y, t1.z ) ) * s0.x * s0.y * s1.z
      + texture( tex, vec3( t1.x, t0.y, t1.z ) ) * s1.x * s0.y * s1.z
      + texture( tex, vec3( t0.x, t1.y, t1.z ) ) * s0.x * s1.y * s1.z
      + texture( tex, vec3( t1.x, t1.y, t1.z ) ) * s1.x * s1.y * s1.z;
}

float reduce_add(vec3 f)
{
  return f.x + f.y + f.z;
}

vec3 sample_spherical_direction(vec2 uv)
{
    float phi = M_2PI * (uv.x - 0.5);
    float theta = M_PI * uv.y;

    vec3 n;
    n.x = cos(phi) * sin(theta);
    n.y = -sin(phi) * sin(theta);
    n.z = -cos(theta);

    return n;
}

vec2 sample_spherical_map(const vec3 d)
{
    vec2 uv = vec2(0.5 - atan(d.z, d.x) * M_1_2PI, 0.5 + asin(d.y) * M_1_PI);
    return uv;
}

/* ------------------------------ SDF Functions ----------------------------- */

float sdf_sphere( vec3 p, float s ) 
{
  return length(p)-s;
}

float sdf_op_sub(float d1, float d2) 
{ 
    return max(-d1,d2); 
}

float sdf_op_smooth_sub( float d1, float d2, float k ) 
{
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h); 
}

/* ------------------------- Intersection Functions ------------------------- */

bool sphere_intersect(Ray ray, vec3 center, float radius, out float t0, out float t1)
{
    precise vec3 l = (ray.pos - center);
    precise float b = dot(ray.dir, l);
    precise vec3 qc = l - b*ray.dir;
    precise float h = radius*radius - dot(qc,qc);

    if (h < 0.0) {
        t0 = -1.0;
        t1 = -1.0;
        return false;
    }

    h = sqrt(h);

    t0 = -b-h;
    t1 = -b+h;

    bool behind = (t0 < 0.0 && t1 < 0.0);

    return !behind;
}

/* ------------------------------- Atmosphere ------------------------------- */

uniform bool enable_atm;
uniform bool enable_moon;
uniform bool enable_sun;

uniform bool enable_moon_as_light;
uniform bool enable_sun_as_light;

uniform Light sun;
uniform Light moon;

uniform float altitude;

uniform float rayleigh_density;
uniform float mie_density;
uniform float ozone_density;

const float earth_radius = 6360e3;
const float atmosphere_radius = 6420e3;
const float mie_coeff = 2e-5;

const float rayleigh_scale_height = 8.0e3;
const float mie_scale_height = 1.2e3;

const float atmo_camera_offset = 1000.0;

const float mie_G = 0.75;

const int num_wavelengths = 21;          
const int min_wavelength = 380;
const int max_wavelength = 780;

const float step_lambda = (max_wavelength - min_wavelength) / (num_wavelengths - 1);

// Sun irradiance on top of the atmosphere (W*m^-2*nm^-1)
uniform float irradiance[21] = float[] (
    1.45756829855592995315f, 1.56596305559738380175f, 1.65148449067670455293f,
    1.71496242737209314555f, 1.75797983805020541226f, 1.78256407885924539336f,
    1.79095108475838560302f, 1.78541550133410664714f, 1.76815554864306845317f,
    1.74122069647250410362f, 1.70647127164943679389f, 1.66556087452739887134f,
    1.61993437242451854274f, 1.57083597368892080581f, 1.51932335059305478886f,
    1.46628494965214395407f, 1.41245852740172450623f, 1.35844961970384092709f,
    1.30474913844739281998f, 1.25174963272610817455f, 1.19975998755420620867f);

// Rayleigh scattering coefficient (m^-1) 
uniform float rayleigh_coeff[21] = float[] (
    0.00005424820087636473f, 0.00004418549866505454f, 0.00003635151910165377f,
    0.00003017929012024763f, 0.00002526320226989157f, 0.00002130859310621843f,
    0.00001809838025320633f, 0.00001547057129129042f, 0.00001330284977336850f,
    0.00001150184784075764f, 0.00000999557429990163f, 0.00000872799973630707f,
    0.00000765513700977967f, 0.00000674217203751443f, 0.00000596134125832052f,
    0.00000529034598065810f, 0.00000471115687557433f, 0.00000420910481110487f,
    0.00000377218381260133f, 0.00000339051255477280f, 0.00000305591531679811f);

// Ozone absorption coefficient (m^-1) 
uniform float ozone_coeff[21] = float[] (
    0.00000000325126849861f, 0.00000000585395365047f, 0.00000001977191155085f,
    0.00000007309568762914f, 0.00000020084561514287f, 0.00000040383958096161f,
    0.00000063551335912363f, 0.00000096707041180970f, 0.00000154797400424410f,
    0.00000209038647223331f, 0.00000246128056164565f, 0.00000273551299461512f,
    0.00000215125863128643f, 0.00000159051840791988f, 0.00000112356197979857f,
    0.00000073527551487574f, 0.00000046450130357806f, 0.00000033096079921048f,
    0.00000022512612292678f, 0.00000014879129266490f, 0.00000016828623364192f);

// CIE XYZ color matching functions
uniform vec3 cmf_xyz[21] = vec3[](
        vec3(0.00136800000f, 0.00003900000f, 0.00645000100f),
        vec3(0.01431000000f, 0.00039600000f, 0.06785001000f),
        vec3(0.13438000000f, 0.00400000000f, 0.64560000000f),
        vec3(0.34828000000f, 0.02300000000f, 1.74706000000f),
        vec3(0.29080000000f, 0.06000000000f, 1.66920000000f),
        vec3(0.09564000000f, 0.13902000000f, 0.81295010000f),
        vec3(0.00490000000f, 0.32300000000f, 0.27200000000f),
        vec3(0.06327000000f, 0.71000000000f, 0.07824999000f),
        vec3(0.29040000000f, 0.95400000000f, 0.02030000000f),
        vec3(0.59450000000f, 0.99500000000f, 0.00390000000f),
        vec3(0.91630000000f, 0.87000000000f, 0.00165000100f),
        vec3(1.06220000000f, 0.63100000000f, 0.00080000000f),
        vec3(0.85444990000f, 0.38100000000f, 0.00019000000f),
        vec3(0.44790000000f, 0.17500000000f, 0.00002000000f),
        vec3(0.16490000000f, 0.06100000000f, 0.00000000000f),
        vec3(0.04677000000f, 0.01700000000f, 0.00000000000f),
        vec3(0.01135916000f, 0.00410200000f, 0.00000000000f),
        vec3(0.00289932700f, 0.00104700000f, 0.00000000000f),
        vec3(0.00069007860f, 0.00024920000f, 0.00000000000f),
        vec3(0.00016615050f, 0.00006000000f, 0.00000000000f),
        vec3(0.00004150994f, 0.00001499000f, 0.00000000000f));

const int quadrature_steps = 8;

uniform float quadrature_nodes[8] = float[8] (
    0.006811185292,
    0.03614807107,
    0.09004346519,
    0.1706680068,
    0.2818362161,
    0.4303406404,
    0.6296271457,
    0.9145252695);

uniform float quadrature_weights[8] = float[8] (
    0.01750893642,
    0.04135477391,
    0.06678839063,
    0.09507698807,
    0.1283416365,
    0.1707430204,
    0.2327233347,
    0.3562490486);

const mat3 xyz_to_rgb = mat3(
     3.2404542, -0.9692660,  0.0556434,
    -1.5371385,  1.8760108, -0.2040259,
    -0.4985314,  0.0415560,  1.0572252
);
uniform float sun_half_angular;
uniform float moon_half_angular;

uniform vec3 moon_phase_dir;
uniform float moon_ambient_intsty;

uniform mat4 moon_rot_mat;

#define MAX_RADIATION 2e6
/* --------------------------------- Clouds --------------------------------- */

uniform bool enable_cld;
uniform bool enable_cld_0;
uniform bool enable_cld_1;

/*
*   cloud domain height at zenith (m): h
*   cloud domain horizon view distance (m): d
*   cloud domain radius (m): r
*   cloud domain center (m): c
*
*   r = (2d)^2 / (8h) + h/2
*   c = <0, 0, h - r>
*/

uniform vec3 cld_domain_center;

uniform int cld_max_steps;
uniform int cld_max_light_steps;

uniform float cld_G;

const float cld_top_roundness = 0.05;
const float cld_btm_roundness = 0.0;

const float cld_top_density = 0.05;
const float cld_btm_density = 0.45;

uniform bool enable_bicubic;

struct Cloud {
    float   radius;
    float   density;
    float   height;
    float   thickness;

    float   powder_intsty;
    float   ap_intsty;
    float   ambient_intsty;

    float   atten;
    float   contr;
    float   eccen;

    float   coverage_shape;

    float   coverage_scale;
    float   shape_scale;
    float   detail_scale;

    float   coverage_intsty;
    float   shape_intsty;
    float   detail_intsty;

    vec2    coverage_offset;
    vec2    shape_offset;
    vec2    detail_offset;

    mat4    transform;
};

uniform Cloud cloud_0;
uniform Cloud cloud_1;
/* -------------------------------------------------------------------------- */
/*                                 ATMOSPHERE                                 */
/* -------------------------------------------------------------------------- */

vec3 spec_to_rgb(float spec[num_wavelengths])
{
    vec3 xyz = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < num_wavelengths; i++) {
        xyz.x += cmf_xyz[i].x * spec[i];
        xyz.y += cmf_xyz[i].y * spec[i];
        xyz.z += cmf_xyz[i].z * spec[i];
    }
    vec3 rgb = xyz_to_rgb * (xyz * step_lambda);
    return rgb;
}

float get_height(vec3 p)
{
    float min_altitude = 0.0;
    float max_altitude = atmosphere_radius-earth_radius;
    return clamp((length(p) - atmo_camera_offset + altitude) - earth_radius, min_altitude, max_altitude);
}

/* ----------------------------- Phase Functions ---------------------------- */

float phase_rayleigh(float mu)
{
    return M_3_16PI * (1.0 + (mu*mu));
}

float phase_mie(float mu, float G)
{
    float sqr_G = G*G;
    return (3.0 * (1.0 - sqr_G) * (1.0 + (mu*mu))) / (8.0 * M_PI * (2.0 + sqr_G) * pow((1.0 + sqr_G - 2.0 * G * mu), 1.5));
}

/* ------------------------ Atmosphere volume models ------------------------ */

float density_rayleigh(float height)
{
  return exp(-height / rayleigh_scale_height);
}

float density_mie(float height)
{
  return exp(-height / mie_scale_height);
}

float density_ozone(float height)
{
  float den = 0.0;
  if (height >= 10000.0 && height < 25000.0) {
    den = 1.0 / 15000.0 * height - 2.0 / 3.0;
  }
  else if (height >= 25000 && height < 40000) {
    den = -(1.0 / 15000.0 * height - 8.0 / 3.0);
  }
  return den;
}

/* ------------------------- Atmosphere Intersection ------------------------ */

bool surface_intersection(Ray ray)
{
    float t0, t1;

    bool hit = sphere_intersect(ray, vec3(0.0), earth_radius, t0, t1);
    bool front = (t0 >= 0 && t1 >= 0);

    return (hit && front);
}

vec3 atmosphere_intersection(Ray ray)
{
    
    float t0, t1;
	bool hit_atmosphere = sphere_intersect(ray, vec3(0.0), atmosphere_radius, t0, t1);

    float s0, s1;
	bool hit_earth = sphere_intersect(ray, vec3(0.0), earth_radius, s0, s1);

    bool earth_front = (s0 > 0 && s1 > 0);

    float t = 0.0;
    if (hit_earth && earth_front) {
        t = s0; 
    } else {
        t = t1;
    }
    return ray.pos + ray.dir * t;
}

/* ----------------------------- Atmosphere Main ---------------------------- */

vec3 ray_optical_depth(Ray ray)
{
    vec3 ray_end = atmosphere_intersection(ray);
    float ray_length = distance(ray.pos, ray_end);

    vec3 segment = ray_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    for (int i = 0; i < quadrature_steps; i++) {
        vec3 pos = ray.pos + quadrature_nodes[i] * segment;

        float height = get_height(pos);
        vec3 density = vec3(density_rayleigh(height), density_mie(height), density_ozone(height));

        optical_depth += density * quadrature_weights[i];
    }
    return optical_depth * ray_length;
}

vec3 atmo_raymarch(Ray ray, Light light) 
{
    /* this code computes single-inscattering along a ray through the atmosphere */
    vec3 ray_end = atmosphere_intersection(ray);
    float ray_length = distance(ray.pos, ray_end);

    float segment_length = ray_length / 64.0;
    vec3 segment = segment_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    /* zero out light accumulation */
    float r_spectrum[num_wavelengths];
    for (int wl = 0; wl < num_wavelengths; wl++) {
        r_spectrum[wl] = 0.0;
    }

    /* phase function for scattering and the density scale factor */
    float mu = dot(ray.dir, light.dir);
    vec3 phase_function = vec3(phase_rayleigh(mu), phase_mie(mu, mie_G), 0.0);
    vec3 density_scale = vec3(rayleigh_density, mie_density, ozone_density);

    /* the density and in-scattering of each segment is evaluated at its middle */
    vec3 pos = ray.pos; float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    {
        pos = ray.pos + march_dst * ray.dir;

        /* height above sea level */
        float height = get_height(pos);

        /* evaluate and accumulate optical depth along the ray */
        vec3 density = density_scale * vec3(density_rayleigh(height),
                                            density_mie(height),
                                            density_ozone(height));

        optical_depth += segment_length * density;

        /* if the Earth isn't in the way, evaluate inscattering from the sun */
        Ray light_ray = Ray(pos, light.dir);
        if (!surface_intersection(light_ray)) {
            vec3 light_optical_depth = density_scale * ray_optical_depth(light_ray);
            vec3 total_optical_depth = optical_depth + light_optical_depth;
            
            for (int wl = 0; wl < num_wavelengths; wl++) {

                vec3 extinction_density = total_optical_depth * vec3(rayleigh_coeff[wl],
                                                                     mie_coeff,
                                                                     ozone_coeff[wl]);

                float attenuation = exp(-reduce_add(extinction_density));
                vec3 scattering_density = density * vec3(rayleigh_coeff[wl], mie_coeff, 0.0);

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * segment_length;
            }
        }
        march_dst += segment_length;
    }
    return spec_to_rgb(r_spectrum);
}

vec3 atmo_raymarch(Ray ray, Light light, vec3 ray_end) 
{
    /* this code computes single-inscattering along a ray through the atmosphere */
    float ray_length = distance(ray.pos, ray_end);

    float segment_length = ray_length / 64.0;
    vec3 segment = segment_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    /* zero out light accumulation */
    float r_spectrum[num_wavelengths];
    for (int wl = 0; wl < num_wavelengths; wl++) {
        r_spectrum[wl] = 0.0;
    }

    /* phase function for scattering and the density scale factor */
    float mu = dot(ray.dir, light.dir);
    vec3 phase_function = vec3(phase_rayleigh(mu), phase_mie(mu, mie_G), 0.0);
    vec3 density_scale = vec3(rayleigh_density, mie_density, ozone_density);

    /* the density and in-scattering of each segment is evaluated at its middle */
    vec3 pos = ray.pos; float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    {
        pos = ray.pos + march_dst * ray.dir;

        /* height above sea level */
        float height = get_height(pos);

        /* evaluate and accumulate optical depth along the ray */
        vec3 density = density_scale * vec3(density_rayleigh(height),
                                            density_mie(height),
                                            density_ozone(height));

        optical_depth += segment_length * density;

        /* if the Earth isn't in the way, evaluate inscattering from the sun */
        Ray light_ray = Ray(pos, light.dir);
        if (!surface_intersection(light_ray)) {

            vec3 light_optical_depth = density_scale * ray_optical_depth(light_ray);
            vec3 total_optical_depth = optical_depth + light_optical_depth;
            
            for (int wl = 0; wl < num_wavelengths; wl++) {

                vec3 extinction_density = total_optical_depth * vec3(rayleigh_coeff[wl],
                                                                     mie_coeff,
                                                                     ozone_coeff[wl]);

                float attenuation = exp(-reduce_add(extinction_density));
                vec3 scattering_density = density * vec3(rayleigh_coeff[wl], mie_coeff, 0.0);

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * segment_length;
            }
        }
        march_dst += segment_length;
    }
    return spec_to_rgb(r_spectrum);
}

vec3 sun_radiation(Ray ray, float solid_angle)
{
    vec3 optical_depth = ray_optical_depth(ray);

    if (!surface_intersection(ray)) {
        float r_spectrum[num_wavelengths];
        for (int wl = 0; wl < num_wavelengths; wl++) {
            r_spectrum[wl] = 0.0;
        }

        /* compute final spectrum */
        for (int i = 0; i < num_wavelengths; i++) {
            /* combine spectra and the optical depth into transmittance */
            float transmittance = rayleigh_coeff[i] * optical_depth.x * rayleigh_density +
                                    1.11f * mie_coeff * optical_depth.y * mie_density;
            r_spectrum[i] = irradiance[i] * exp(-transmittance) / solid_angle;
        }

        return spec_to_rgb(r_spectrum);
    } else {
        return vec3(0.0);
    }
}
/* ---------------------------- Celestial Objects --------------------------- */

const float moon_dist = 500.0;

bool hit_moon(vec3 dir)
{
    Ray ray = Ray(vec3(0.0), dir);

    vec3 moon_pos = moon.dir * moon_dist;
    float moon_radius = (moon_half_angular * 1.05) * moon_dist;

    float t0, t1;
    return sphere_intersect(ray, moon_pos, moon_radius, t0, t1);
}

vec4 draw_moon(Ray ray) 
{
    vec4 color = vec4(0.0);

    Ray moon_ray = Ray(vec3(0.0), ray.dir);

    vec3 moon_pos = moon.dir * moon_dist;
    float moon_radius = moon_half_angular * moon_dist;

    float t0, t1;
    if (sphere_intersect(moon_ray, moon_pos, moon_radius, t0, t1)) 
    {
        vec3 sphere_pos = moon_ray.pos + moon_ray.dir * t0;
        vec3 sphere_norm = normalize(sphere_pos-moon_pos);

        vec3 _sphere_norm = normalize(vec3(moon_rot_mat * vec4(sphere_norm, 0.0)));
        vec2 uv = sample_spherical_map(_sphere_norm);

        vec3 norm = texture(moon_normal_tex, uv).rgb;
        norm = norm * 2.0 - 1.0;

        vec3 T = vec3(-sphere_norm.y, sphere_norm.x, 0.0);
        vec3 B = cross(T, sphere_norm);
        norm = normalize(T*norm.x + B*norm.y + sphere_norm*norm.z);

        float moon_solid_angle = M_2PI * (1.0 - cos(0.5 * moon_half_angular));
        vec3 L = min(sun_radiation(ray, moon_solid_angle) * 0.00025 * moon.intsty, MAX_RADIATION);

        float diff = max(dot(moon_phase_dir, norm), 0.0);
        color = vec4(L * (diff + moon_ambient_intsty) * texture(moon_albedo_tex, uv).rgb, 1.0);
    }
    return color;
}

vec4 draw_sun(Ray ray) 
{
    vec4 color = vec4(0.0);
    float min_cos_theta = cos(sun_half_angular);

    float cos_theta = dot(ray.dir, sun.dir);
    if (cos_theta >= min_cos_theta) {
        color = vec4(1.0);
    } else {
        float offset = min_cos_theta - cos_theta;
        float scale_factor = 3000.0 / (sun_half_angular*2.0);
        float gaussian_bloom = exp(-offset*scale_factor);
        color = vec4(gaussian_bloom);
    }

    if (color.a > 0.00001) {
        float sun_solid_angle = M_2PI * (1.0 - cos(0.5 * sun_half_angular));
        vec3 L = min(sun_radiation(ray, sun_solid_angle) * sun.intsty, MAX_RADIATION);
        color.rgb *= L;
    }
    return color;
}
/* -------------------------------------------------------------------------- */
/*                                   CLOUDS                                   */
/* -------------------------------------------------------------------------- */

void shell_intersection(Ray ray, vec3 center, float radius_inner, float radius_outer, out float t_start, out float t_end) 
{
    t_start = 0.0;
    t_end = 0.0;

    float t0, t1;
    bool hit_outer = sphere_intersect(ray, center, radius_outer, t0, t1);

    float s0, s1;
    bool hit_inner = sphere_intersect(ray, center, radius_inner, s0, s1);

    t_start = (hit_inner) ? s1 : 0.0;
    t_end = (hit_outer) ? t1 : 0.0;
}

bool cld_sample( 
    Cloud cloud,
    vec3 pos,
    out float ds, 
    out float dist, 
    out float p_h) 
{
    float inner_shell = sdf_sphere(pos, cloud.radius);
    float outer_shell = sdf_sphere(pos, cloud.radius + cloud.thickness);
    float cld_shell = sdf_op_sub(inner_shell, outer_shell);

    ds = 0.0;
    dist = 0.0;
    p_h = 0.0;

    bool hit = false;

    if (cld_shell < 0.0) {
        p_h = saturate(clamp(length(pos) - cloud.radius, 0.0, cloud.thickness) / (cloud.thickness));
        
        vec2 c_sp = (pos.xy + cloud.coverage_offset) * cloud.coverage_scale;
        vec4 cns = (enable_bicubic) ? bicubic_sample(noise_tex_2D_2048, c_sp, vec2(2048)) : texture(noise_tex_2D_2048, c_sp);

        vec3 s_sp = (pos + vec3(cloud.coverage_offset + cloud.shape_offset, 0.0)) * cloud.shape_scale;
        vec4 sns = (enable_bicubic) ? bicubic_sample(noise_tex_3D_128, s_sp, vec3(128)) : texture(noise_tex_3D_128, s_sp);

        vec3 d_sp = (pos + vec3(cloud.coverage_offset + cloud.detail_offset, 0.0)) * cloud.detail_scale;
        vec4 dns = (enable_bicubic) ? bicubic_sample(noise_tex_3D_64, d_sp, vec3(64)) : texture(noise_tex_3D_64, d_sp);

        float CN = mix(cns.x, cns.y, cloud.coverage_shape);

        float wh = CN * cloud.height;

        float SR_b = saturate(remap(p_h, 0.0, cld_btm_roundness, 0.0, 1.0));
        float SR_t = saturate(remap(p_h, wh*cld_top_roundness, wh, 1.0, 0.0));
        
        float DR_b = saturate(remap(p_h, 0.0, cld_btm_density, 0.0, 1.0));
        float DR_t = saturate(remap(p_h, cld_top_density, 1.0, 1.0, 0.0));
            
        float SA = SR_b * SR_t;
        float DA = DR_b * DR_t;

        float DN = dns.r*0.625+dns.g*0.25+dns.b*0.125;
        float SN = sns.g*0.625+sns.b*0.25+sns.a*0.125;

        float cld_coverage = remap(CN * cloud.coverage_intsty * SA, 0.0, 1.0, -1.0, 1.0);
        float cld_shape = SN * cloud.shape_intsty;
        //float cld_shape = mix(SN-1, SN, saturate(p_h*5.0)) * cloud.shape_intsty;
        float cld_detail = DN * cloud.detail_intsty;
        //float cld_detail = mix(DN-1, DN, saturate(p_h*5.0)) * cloud.detail_intsty;

        cld_shell = sdf_op_sub(cld_coverage, cld_shell);
        cld_shell = clamp(cld_detail + cld_shape, -1.0, 1.0) + cld_shell;

        if (cld_shell < 0.f) {
            ds = cloud.density * min(abs(cld_shell), 1.0) * DA;
            dist = cld_shell;
            hit = true;
        } else {
            ds = 0.0;
            dist = cld_shell;
            hit = false;
        }
    }

    return hit;
}

bool cloud_density(
    Cloud cloud,
    vec3 pos, 
    out float sigma_s, 
    out float sigma_t, 
    out float dist, 
    out float p_h) 
{
    sigma_t = 0.0;
    sigma_s = 0.0;
    dist = 0.0;
    p_h = 0.0;

    vec3 t_pos = vec3(cloud.transform * vec4(pos, 1.0));
    bool hit = cld_sample(cloud, t_pos, sigma_s, dist, p_h);

    sigma_t = max(0.000000001, sigma_s);

    return hit;
}

float shadow_raymarch(Cloud cloud, Ray ray, vec3 light_dir)
{
    float shadow = 1.0;

    Ray light_ray;
    light_ray.pos = ray.pos;
    light_ray.dir = light_dir;

    float t_start, t_end;
    shell_intersection(
        ray, 
        cld_domain_center + vec3(0, 0, earth_radius), 
        cloud.radius, 
        cloud.radius + cloud.thickness, 
        t_start, 
        t_end);

    if (!surface_intersection(light_ray)) {
        vec3 start_pos = (light_ray.pos + light_ray.dir * t_start);
        vec3 end_pos = (light_ray.pos + light_ray.dir * t_end);
        float ray_length = distance(start_pos, end_pos);
    
        ray_length = min(ray_length, 5000);

        float step_size_orig = ray_length / cld_max_light_steps;
        float step_size = step_size_orig;

        float d = 0.0;

        float march_dst = 0.0;
        for (int i = 0; i < cld_max_light_steps; i++)
        {
            vec3 pos = ray.pos + light_dir*march_dst;

            float sigma_s, sigma_t, dist, p_h;
            bool in_cloud = cloud_density(cloud, pos, sigma_s, sigma_t, dist, p_h);
            if (in_cloud) {
                d += sigma_t * step_size;

                if (exp(d) < 1e-5) {
                    shadow = 0.0;
                    return 0.0;
                }
            }

            step_size = in_cloud ? step_size_orig : max(dist, step_size_orig);
            march_dst += step_size;
        }

        float beer = (exp(-d));
        float powder = (1.0 - exp(-d * cloud.powder_intsty));
        float shadow = beer * powder;
        return shadow;
    } else {
        return 0.0;
    }
}

vec3 int_ambient_light(Cloud cloud, float sigma_s, float sigma_t, float p_h, float step_size) 
{
    vec2 uv = clamp(vec2(0.5, p_h), vec2(0.01), vec2(1.0));
    vec3 ambient_color = texture(irra_tex, uv).rgb * cloud.ambient_intsty;
    vec3 scatter = sigma_s * ambient_color;
    vec3 s_int = (scatter - scatter * exp(-sigma_t * step_size)) / sigma_t;

    return s_int;
}

vec3 int_direct_light(Cloud cloud, Ray ray, Light light, float sigma_s, float sigma_t, float step_size)
{
    Ray light_ray;
    light_ray.pos = ray.pos;
    light_ray.dir = light.dir;
    
    float vis = shadow_raymarch(cloud, ray, light.dir);

    if (vis > 0.00001) {
        vec3 L = sun_radiation(light_ray, 1.0);
        float mu = dot(light.dir, ray.dir);

        /* Multiple scattering approximation: DOI: 10.1145/2504459.2504518 */
        vec3 s_int = vec3(0.0);
        for (int i = 0; i < 8; i++) 
        {
            float _ai = pow(cloud.atten, i); /* attenuation */
            float _bi = pow(cloud.contr, i); /* contribution */
            float _ci = pow(cloud.eccen, i); /* eccentricity attenuation */

            float x = phase_mie(mu, cld_G * _ci);
            float y = light.silver_intsty * phase_mie(mu, (0.99 - light.silver_spread) * _ci);
            float _phase = max(x,y);

            vec3 Li = sigma_s * _bi * L * _phase * exp(-_ai * sigma_t * step_size);
            s_int += (Li - Li *  exp(-sigma_t * step_size)) / sigma_t;
        }

        return s_int * vis;
    } else {
        return vec3(0.0);
    }
}

vec3 cloud_raymarch(Cloud cloud, Ray ray, out float depth, out float opacity) 
{
    depth = 0.0;
    opacity = 0.0;

    float transmittance = 1.0;
    vec3 scattered_light = vec3(0.0, 0.0, 0.0);

    float t_start, t_end;
    shell_intersection(
        ray, 
        cld_domain_center + vec3(0, 0, earth_radius), 
        cloud.radius - 500.0, 
        cloud.radius + cloud.thickness + 500.0, 
        t_start, 
        t_end);

    vec2 uv = gl_FragCoord.xy / img_size.xy;

    float noise_offset = 2.0 * texture(blue_noise, uv*32.0).r - 1.0;
    noise_offset *= 500.0;

    vec3 start_pos = (ray.pos + ray.dir * (t_start + noise_offset));
    vec3 end_pos = (ray.pos + ray.dir * (t_end + noise_offset));
    float ray_length = distance(start_pos, end_pos);

    depth = distance(ray.pos, end_pos);

    if (surface_intersection(ray)) return scattered_light;

    float segment_length = ray_length / float(cld_max_steps);
    float segment = segment_length;

    float march_dst = 0.0;
    for (int i = 0; i < cld_max_steps; i++) {
        ray.pos = start_pos + march_dst * ray.dir;

        float sigma_s, sigma_t, dist, p_h;
        bool in_cloud = cloud_density(cloud, ray.pos, sigma_s, sigma_t, dist, p_h);

        if (in_cloud) 
        {
            vec3 direct_light = vec3(0.0);
            direct_light += (enable_sun && enable_sun_as_light) ? int_direct_light(cloud, ray, sun, sigma_s, sigma_t, segment) : vec3(0.0);
            direct_light += (enable_moon && enable_moon_as_light) ? int_direct_light(cloud, ray, moon, sigma_s, sigma_t, segment) * 0.00025 : vec3(0.0);
            vec3 ambient_light = int_ambient_light(cloud, sigma_s, sigma_t, p_h, segment);

            transmittance *= exp(-sigma_t * segment);
            scattered_light += transmittance * (direct_light + ambient_light);
        }

        if (transmittance < 1e-7) {
            transmittance = 0.0;
            break;
        }

        segment = in_cloud ? segment_length : max(dist, segment_length);
        march_dst += segment;
    }

    opacity = 1.0 - transmittance;

    return scattered_light;
}

out vec4 fragColor;

uniform mat4 inv_vp_mat;

vec4 compute_cld(Cloud cloud, Ray ray, vec4 atmo_color, out float cld_opacity)
{
    float   cld_depth     = 0.0;
    vec4    cld_color     = vec4(0.0);

    cld_color = vec4(cloud_raymarch(cloud, ray, cld_depth, cld_opacity), 1.0);
    float ap_clouds = exp(-cld_depth / cloud.ap_intsty);

    cld_color = vec4(mix(atmo_color.rgb, cld_color.rgb, ap_clouds), 1.0);

    return cld_color;
}

void main()
{       
    if (gl_FragCoord.x > img_size.x || gl_FragCoord.y > img_size.y) return;

    /* ------------------------------- Set up ray ------------------------------- */

    vec2 p_NDC; // [-1, 1] x [-1, 1]
    p_NDC.x = 2.0 * ((gl_FragCoord.x + 0.5) / img_size.x) - 1.0;
    p_NDC.y = 2.0 * ((gl_FragCoord.y + 0.5) / img_size.y) - 1.0;

    vec4 p_near_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, -1.0, 1.0);
    vec4 p_far_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, 1.0, 1.0);

    vec3 p_near = vec3(p_near_NDC.xyz) / p_near_NDC.w;
    vec3 p_far = vec3(p_far_NDC.xyz) / p_far_NDC.w;

    Ray ray;
    ray.pos = vec3(0.0, 0.0, earth_radius + atmo_camera_offset);
    ray.dir = normalize(p_far - p_near);

    /* ---------------------------- Render Atmosphere --------------------------- */

    vec4 atmo_color = vec4(0.0);
    atmo_color += (enable_atm && enable_sun && enable_sun_as_light) ? vec4(atmo_raymarch(ray, sun),1.0) : vec4(0.0);
    atmo_color += (enable_atm && enable_moon && enable_moon_as_light) ? vec4(atmo_raymarch(ray, moon),1.0) * 0.000025 : vec4(0.0);    
    
    vec4 sun_color = (enable_sun) ? draw_sun(ray) : vec4(0.0);
    vec4 moon_color = (enable_moon) ? draw_moon(ray) : vec4(0.0);

    vec4 moon_sun_color = vec4(mix(sun_color.rgb, moon_color.rgb, moon_color.a), 1.0);

    /* ------------------------------ Render Clouds ----------------------------- */
    
    vec4 sky_color = vec4(0.0);
    
    if (enable_cld) {

        float cld_0_opacity = 0.0;
        float cld_1_opacity = 0.0;

        vec4 cld_0_color = vec4(0.0);
        vec4 cld_1_color = vec4(0.0);

        if (enable_cld_0) cld_0_color = compute_cld(cloud_0, ray, atmo_color, cld_0_opacity);
        if (enable_cld_1) cld_1_color = compute_cld(cloud_1, ray, atmo_color, cld_1_opacity);

        atmo_color += moon_sun_color;

        sky_color = vec4(mix(atmo_color.rgb, cld_0_color.rgb, cld_0_opacity), 1.0);
        sky_color = vec4(mix(sky_color.rgb, cld_1_color.rgb, cld_1_opacity), 1.0);

    } else {
        sky_color = atmo_color + moon_sun_color;
    }

    /* --------------------------------- Send it -------------------------------- */

    fragColor = sky_color;
}


