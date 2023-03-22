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

uniform sampler3D noise_tex_3D_32;
uniform sampler3D noise_tex_3D_128;
uniform sampler2D noise_tex_2D_1024;
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

    //vec2 _uv = uv * tex_size;
    //vec2 tc = floor( _uv - 0.5 ) + 0.5;
    //vec2 f = _uv - tc;

    vec2 tc = uv * tex_size - 0.5;
    vec2 f = fract(tc);
    tc -= f;
 
    //we'll need the second and third powers
    //of f to compute our filter weights
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

    //vec3 _uvw = uvw * tex_size;
    //vec3 tc = floor( _uvw - 0.5 ) + 0.5;
    //vec3 f = _uvw - tc;

    vec3 tc = mod(uvw, vec3(1.0)) * tex_size - 0.5;
    vec3 f = fract(tc);
    tc -= f;
 
    //we'll need the second and third powers
    //of f to compute our filter weights
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
/* https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm */

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

bool solve_quadratic(float b, float c, float d, out float t0, out float t1) 
{
    if (d > 0.0) {
        float q = (b > 0) ?
            -0.5 * (b + sqrt(d)) :
            -0.5 * (b - sqrt(d));
        t0 = q;
        t1 = c / q;
    } else if (d == 0.0) {
        t0 = t1 = -0.5*b; 
    } else {
        return false;
    }
    if (t0 > t1) {
        float tmp = t0;
        t0 = t1;
        t1 = tmp;
    }
    return true;
}

bool sphere_intersect(Ray ray, vec3 center, float radius, out float t0, out float t1)
{
    vec3 l = (ray.pos - center);

    float b = 2.0*dot(ray.dir, l);
    float c = dot(l, l) - (radius * radius);
    float d = (b * b) - 4.0*c;

    bool sol = solve_quadratic(b, c, d, t0, t1);
    bool behind = (t0 < 0.0 && t1 < 0.0);

    return (sol && !behind);
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

uniform float cld_domain_min_radius;
uniform float cld_domain_max_radius;
uniform vec3 cld_domain_center;

uniform float cld_top_roundness;// = 0.15;
uniform float cld_btm_roundness;// = 0.01;

uniform float cld_top_density;// = 1.0;
uniform float cld_btm_density;// = 0.45;

uniform float cld_ap_intsty;

uniform float cld_ambient_intsty;

uniform int cld_max_steps;
uniform int cld_max_light_steps;

const float cld_G = 0.0;

/* ------------------------------ Cloud Layer 0 ----------------------------- */

uniform float   cld_0_radius;
uniform float   cld_0_density;
uniform float   cld_0_height;
uniform float   cld_0_size;
uniform float   cld_0_detail_intsty;
uniform float   cld_0_shape_intsty;
uniform float   cld_0_coverage_intsty;

uniform vec2    cld_0_detail_offset;
uniform vec2    cld_0_shape_offset;
uniform vec2    cld_0_coverage_offset;

uniform mat4    cld_0_transform;

/* ------------------------------ Cloud Layer 1 ----------------------------- */

uniform float   cld_1_radius;
uniform float   cld_1_density;
uniform float   cld_1_height;
uniform float   cld_1_size;
uniform float   cld_1_detail_intsty;
uniform float   cld_1_shape_intsty;
uniform float   cld_1_coverage_intsty;

uniform vec2    cld_1_detail_offset;
uniform vec2    cld_1_shape_offset;
uniform vec2    cld_1_coverage_offset;

uniform mat4    cld_1_transform;

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

float phase_mie_2(float mu, float G)
{
    float sqr_G = G*G;
    return M_1_4PI * ((1.0 - sqr_G) / pow((1.0 + sqr_G-(2.0 * G * mu)), 1.5));
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

vec3 atmo_raymarch(Ray ray, Light light, float ls) 
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
    //vec3 pos = ray.pos + 0.5 * segment;
    vec3 pos = ray.pos;// + 0.5 * segment;
    float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    //for (float march_dst = 0.0; march_dst < ray_length; march_dst += segment_length)
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

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * ls * segment_length;
            }
            
        }
        //pos += segment;
        march_dst += segment_length;
    }
    return spec_to_rgb(r_spectrum);
}

vec3 atmo_raymarch(Ray ray, Light light, vec3 ray_end, float ls) 
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
    //vec3 pos = ray.pos + 0.5 * segment;
    vec3 pos = ray.pos;// + 0.5 * segment;
    float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    //for (float march_dst = 0.0; march_dst < ray_length; march_dst += segment_length)
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

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * ls * segment_length;
            }
            
        }
        //pos += segment;
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

vec3 moon_radiation(Ray ray, float solid_angle)
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
            r_spectrum[i] = irradiance[i] * 0.0034 * exp(-transmittance) / solid_angle;
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
    float moon_radius = (moon_half_angular*1.05) * moon_dist;

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
        vec3 L = sun_radiation(ray, moon_solid_angle) * 0.00025 * moon.intsty;

        float diff = max(dot(moon_phase_dir, norm),0.0);
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
        vec3 L = sun_radiation(ray, sun_solid_angle) * sun.intsty;
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

    //if (!surface_intersection(ray)) {
        float t0, t1;
        bool hit_outer = sphere_intersect(ray, center, radius_outer, t0, t1);

        float s0, s1;
        bool hit_inner = sphere_intersect(ray, center, radius_inner, s0, s1);

        t_start = (hit_inner) ? s1 : 0.0;
        t_end = (hit_outer) ? t1 : 0.0;
    //}
}
/*
bool cld_sample(
    in vec3 p, 
    in float radius, 
    in float density, 
    in float height, 
    in float thickness,
    in float coverage_intsty, 
    in float shape_intsty, 
    in float detail_intsty,
    in float coverage_scale,
    in float shape_scale,
    in float detail_scale,
    in vec2 coverage_offset,
    in vec2 shape_offset,
    in vec2 detail_offset,
    out float ds, 
    out float dist, 
    out float p_h) 
{
    bool hit = false;
    ds = 0.0;
  
    float inner_shell = sdf_sphere(p, radius);
    float outer_shell = sdf_sphere(p, radius + thickness);
    float cld_shell = sdf_op_sub(inner_shell, outer_shell);

    p_h = 1.0;//cld_height_pc(p, radius, radius + thickness);

    if (cld_shell < 0.0) 
    {
        float wh = texture(noise_tex_2D_1024, (p.xy + coverage_offset) * coverage_scale).r * height;

        //float SR_b = saturate(remap(p_h, 0.0, cld_btm_roundness, 0.0, 1.0));
        //float SR_t = saturate(remap(p_h, wh*cld_top_roundness, wh, 1.0, 0.0));
        
        //float DR_b = saturate(remap(p_h, 0.0, cld_btm_density, 0.0, 1.0));
        //float DR_t = saturate(remap(p_h, cld_top_density, 1.0, 1.0, 0.0));
            
        //float SA = SR_b * SR_t;
        //float DA = DR_b * DR_t;

        float blur = 0.001;
        vec2 grad = rndC(vec2(blur, blur));

        vec2 q = ((p.xy + coverage_offset) * coverage_scale);
        vec4 cns = 
            (textureGrad(noise_tex_2D_1024, (q + .5 * vec2(blur, blur)), grad, grad) * .25 + 
            textureGrad(noise_tex_2D_1024, (q + .5 * vec2(blur, -blur)), grad, grad) * .25 + 
            textureGrad(noise_tex_2D_1024, (q + .5 * vec2(-blur, blur)), grad, grad) * .25 + 
            textureGrad(noise_tex_2D_1024, (q + .5 * vec2(-blur, -blur)), grad, grad) * .25);
        
        vec4 sns = texture(noise_tex_3D_128, (p + vec3(shape_offset, 0.0) * shape_scale));
        vec4 dns = texture(noise_tex_3D_32, (p + vec3(detail_offset, 0.0) * detail_scale));

        float DN = dns.r*0.625+dns.g*0.25+dns.b*0.125;
        float SN = sns.g*0.625+sns.b*0.25+sns.a*0.125;

        float asf = remap(p_h, 0.0, 0.5, 0.0, 1.0);
        float test = mix(coverage_intsty*1.2, coverage_intsty, asf);

        float cld_coverage = remap(cns.x * coverage_intsty, 0.0, 1.0, -1.0, 1.0);
        float cld_shape = SN * shape_intsty;
        float cld_detail = mix(DN-1, DN, saturate(p_h*5.0)) * detail_intsty;
        
        ds = density * (cld_coverage + cld_shape + cld_detail);
        hit = true;
    }

    dist = cld_shell;
    return hit;
}
*/

uniform float coverage_interpo;

bool cld_sample(
    in vec3 p, 
    in float radius, 
    in float density, 
    in float height, 
    in float thickness,
    in float coverage_intsty, 
    in float shape_intsty, 
    in float detail_intsty,
    in float coverage_scale,
    in float shape_scale,
    in float detail_scale,
    in vec2 coverage_offset,
    in vec2 shape_offset,
    in vec2 detail_offset,
    out float ds, 
    out float dist, 
    out float p_h) 
{
    //float scale = mix(1.0, 7.5, cld_1_size);
    //float thickness = 1000 * scale;

    //float detail_scale = mix(0.002, 0.01, cld_1_size) / scale;
    //float shape_scale = 0.001 / scale;
    //float coverage_scale = 0.00005 / scale;

    //vec3 p1 = vec3(cld_1_transform*vec4(p, 1.0));

    float inner_shell = sdf_sphere(p, radius);
    float outer_shell = sdf_sphere(p, radius + thickness);
    //float cld_shell = sdf_op_smooth_sub(inner_shell, outer_shell, 0.1);
    float cld_shell = sdf_op_sub(inner_shell, outer_shell);

    bool hit = false;
    ds = 0.0;
    if (cld_shell < 0.0) {
        p_h = saturate(clamp(length(p) - radius, 0.0, thickness) / (thickness));
        
        //vec4 cns = texture(noise_tex_2D_1024, (p.xy + coverage_offset) * coverage_scale);
        vec4 cns = bicubic_sample(noise_tex_2D_1024, (p.xy + coverage_offset) * coverage_scale, vec2(2048.0));
        float foobar = mix(cns.x, cns.y, coverage_interpo);

        float wh = foobar * height;

        float SR_b = saturate(remap(p_h, 0.0, cld_btm_roundness, 0.0, 1.0));
        float SR_t = saturate(remap(p_h, wh*cld_top_roundness, wh, 1.0, 0.0));
        
        float DR_b = saturate(remap(p_h, 0.0, cld_btm_density, 0.0, 1.0));
        float DR_t = saturate(remap(p_h, cld_top_density, 1.0, 1.0, 0.0));
            
        float SA = SR_b * SR_t;
        float DA = DR_b * DR_t;

        //vec4 sns = texture(noise_tex_3D_128, ((p + vec3(shape_offset, 0.0)) * shape_scale));
        vec4 sns = bicubic_sample(noise_tex_3D_128, ((p + vec3(shape_offset, 0.0)) * shape_scale), vec3(128.0));
        //vec4 dns = texture(noise_tex_3D_32, ((p + vec3(detail_offset, 0.0)) * detail_scale));
        vec4 dns = bicubic_sample(noise_tex_3D_32, ((p + vec3(detail_offset, 0.0)) * detail_scale), vec3(64.0));

        float DN = dns.r*0.625+dns.g*0.25+dns.b*0.125;
        float SN = sns.g*0.625+sns.b*0.25+sns.a*0.125;

        float cld_coverage = remap(foobar * coverage_intsty * SR_t * SR_b, 0.0, 1.0, -1.0, 1.0);
        float cld_shape = SN * shape_intsty;
        //float cld_shape = mix(SN-1, SN, saturate(p_h*5.0)) * shape_intsty;
        float cld_detail = DN * detail_intsty;
        //float cld_detail = mix(DN-1, DN, saturate(p_h*5.0)) * detail_intsty;

        cld_shell = sdf_op_sub(cld_coverage, cld_shell);
        cld_shell = cld_detail + cld_shape + cld_shell;

        if (cld_shell < 0.f) {
            ds = density * min(abs(cld_shell), 1.0) * DA;
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

bool cloud_density(in vec3 p, out float sigma_s, out float sigma_t, out float dist, out float p_h) 
{
    float scale, detail_scale, shape_scale, coverage_scale, thickness;

    float cld_0_dist, cld_0_ds, cld_0_ph;
    float cld_1_dist, cld_1_ds, cld_1_ph;

    bool hit_0, hit_1;

    if (enable_cld_0) {
        scale = mix(29, 100, cld_0_size);
        detail_scale = 0.005 / scale;
        shape_scale = 0.0005 / scale;
        coverage_scale = 0.00001 / scale;
        thickness = 1000 * scale;

        vec3 p0 = vec3(cld_0_transform*vec4(p, 1.0));

        hit_0 = cld_sample(
            p0, 
            cld_0_radius,
            cld_0_density,
            cld_0_height*.1,
            thickness,
            cld_0_coverage_intsty,
            cld_0_shape_intsty,
            cld_0_detail_intsty,
            coverage_scale,
            shape_scale,
            detail_scale,
            cld_0_coverage_offset*scale,
            cld_0_shape_offset*scale,
            cld_0_detail_offset*scale,
            cld_0_ds,
            cld_0_dist,
            cld_0_ph
        );
    }

    if (enable_cld_1) {
        scale = mix(1.0, 7.5, cld_1_size);
        detail_scale = 0.001 / scale;
        shape_scale = 0.0003 / scale;
        coverage_scale = 0.00003 / scale;
        thickness = 1000 * scale;

        vec3 p1 = vec3(cld_1_transform*vec4(p, 1.0));

        hit_1 = cld_sample(
            p1, 
            cld_1_radius,
            cld_1_density,
            cld_1_height,
            thickness,
            cld_1_coverage_intsty,
            cld_1_shape_intsty,
            cld_1_detail_intsty,
            coverage_scale,
            shape_scale,
            detail_scale,
            cld_1_coverage_offset*scale,
            cld_1_shape_offset*scale,
            cld_1_detail_offset*scale,
            cld_1_ds,
            cld_1_dist,
            cld_1_ph
        );
    }

    if (hit_0) {
        dist = cld_0_dist;
        p_h = cld_0_ph;
        sigma_s = cld_0_ds;
    }
    else if (hit_1) {
        dist = cld_1_dist;
        p_h = cld_1_ph;
        sigma_s = cld_1_ds;
    }
    else {
        dist = 0.0;
        p_h = 0.0;
        sigma_s = 0.0;
    }

    sigma_t = max(0.000000001, sigma_s);

    return (hit_0 || hit_1);
}

float shadow_raymarch(Ray ray, vec3 light_dir)
{
    float shadow = 1.0;

    Ray light_ray;
    light_ray.pos = ray.pos;
    light_ray.dir = light_dir;

    float t_start, t_end;
    shell_intersection(
        light_ray, 
        cld_domain_center + vec3(0,0,earth_radius), 
        cld_domain_min_radius, 
        cld_domain_max_radius, 
        t_start, 
        t_end);

    if (!surface_intersection(light_ray)) {
        vec3 start_pos = (light_ray.pos + light_ray.dir * t_start);
        vec3 end_pos = (light_ray.pos + light_ray.dir * t_end);
        float ray_length = distance(start_pos, end_pos);
    
        ray_length = min(ray_length, 5000);

        float step_size_orig = ray_length / cld_max_light_steps;
        float step_size = step_size_orig;

        float march_dst = 0.0;
        for (int i = 0; i < cld_max_light_steps; i++)
        {
            vec3 pos = ray.pos + light_dir*march_dst;

            float sigma_s, sigma_t, dist, p_h;
            bool in_cloud = cloud_density(pos, sigma_s, sigma_t, dist, p_h);

            if (in_cloud) {
                shadow *= exp(-sigma_t * step_size);
                if (shadow < 1e-5) {
                    shadow = 0.0;
                    break;
                }
            }

            step_size = in_cloud ? step_size_orig : max(dist, step_size_orig);
            march_dst += step_size;
        }
        return shadow;
    } else {
        return 0.0;
    }
}

vec3 int_ambient_light(in float sigma_s, in float sigma_t, in float p_h, in float step_size) 
{
    vec2 uv = clamp(vec2(0.5, p_h), vec2(0.01), vec2(1.0));
    vec3 ambient_color = texture(irra_tex, uv).rgb * cld_ambient_intsty;
    vec3 scatter = sigma_s * ambient_color;
    vec3 s_int = (scatter - scatter * exp(-sigma_t * step_size)) / sigma_t;

    return s_int;
}

vec3 int_direct_light(in Ray ray, in Light light, in float sigma_s, in float sigma_t, in float step_size)
{
    Ray light_ray;
    light_ray.pos = ray.pos;
    light_ray.dir = light.dir;
    
    float vis = shadow_raymarch(ray, light.dir);

    if (vis > 0.00001) {
        float sun_solid_angle = M_2PI * (1.0 - cos(0.5 * sun_half_angular));
        vec3 L = sun_radiation(light_ray, 1.0);

        float mu = dot(light.dir, ray.dir);

        vec3 s_int = vec3(0.0);
        for (int i = 0; i < 8; i++) 
        {
            float _pow_i = pow(0.5, i);
            float _ai = _pow_i; /* attenuation */
            float _bi = _pow_i; /* contribution */
            float _ci = _pow_i; /* eccentricity attenuation */

            float x = phase_mie(mu, cld_G * _ci);
            float y = light.silver_intsty * phase_mie(mu, (0.99 - light.silver_spread) * _ci);
            float _phase = max(x,y);

            /* Multiple scattering approximation: DOI: 10.1145/2504459.2504518 */
            vec3 Li = sigma_s * _bi * L * _phase * exp(-_ai * sigma_t * step_size);
            s_int += (Li - Li * exp(-sigma_t * step_size)) / sigma_t;
        }
        return s_int * vis;
    } else {
        return vec3(0.0);
    }
}

vec3 cloud_raymarch(Ray ray, out float depth, out float opacity) 
{
    depth = 0.0;
    opacity = 0.0;

    float transmittance = 1.0;
    vec3 scattered_light = vec3(0.0, 0.0, 0.0);

    float t_start, t_end;
    shell_intersection(
        ray, 
        cld_domain_center + vec3(0, 0, earth_radius), 
        cld_domain_min_radius, 
        cld_domain_max_radius, 
        t_start, 
        t_end);

    vec2 uv = gl_FragCoord.xy / img_size.xy;

    //vec2 _uv = mod(uv*16.0, vec2(1.0,1.0));

    float noise_offset = 2.0 * texture(blue_noise, uv*16.0).r - 1.0;
    noise_offset *= 5000.0;

    vec3 start_pos = (ray.pos + ray.dir * (t_start + noise_offset));
    vec3 end_pos = (ray.pos + ray.dir * t_end);
    float ray_length = distance(start_pos, end_pos);

    depth = distance(ray.pos, end_pos);

    if (surface_intersection(ray)) return scattered_light;

    float segment_length = ray_length / float(cld_max_steps);
    float segment = segment_length;

    float march_dst = 0.0;
    for (int i = 0; i < cld_max_steps; i++) {
        ray.pos = start_pos + march_dst * ray.dir;

        float sigma_s, sigma_t, dist, p_h;
        bool in_cloud = cloud_density(ray.pos, sigma_s, sigma_t, dist, p_h);

        if (in_cloud) 
        {
            vec3 direct_light = vec3(0.0);
            direct_light += (enable_sun && enable_sun_as_light) ? int_direct_light(ray, sun, sigma_s, sigma_t, segment) : vec3(0.0);
            direct_light += (enable_moon && enable_moon_as_light) ? int_direct_light(ray, moon, sigma_s, sigma_t, segment) * 0.00025 : vec3(0.0);
            vec3 ambient_light = int_ambient_light(sigma_s, sigma_t, p_h, segment);

            transmittance *= exp(-sigma_t * segment);
            scattered_light += transmittance * (direct_light + ambient_light);
        }

        //if (transmittance < 1e-5) {
        //    transmittance = 0.0;
        //    break;
        //}

        segment = in_cloud ? segment_length : max(dist, segment_length);
        march_dst += segment;
    }
    opacity = 1.0 - transmittance;

    return scattered_light;
}

out vec4 fragColor;

uniform mat4 inv_vp_mat;

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

    /* ------------------------------ Render Clouds ----------------------------- */
    float cld_opacity, cld_depth;
    vec4 cld_color = enable_cld ? vec4(cloud_raymarch(ray, cld_depth, cld_opacity), 1.0) : vec4(0.0);

    vec3 cld_point = ray.pos + ray.dir * (cld_depth * 0.90);
    vec4 cld_ap = vec4(atmo_raymarch(ray, sun, cld_point, 1.0),1.0);
    float ap_clouds = exp(-cld_depth/cld_ap_intsty);

    cld_color = mix(cld_ap, cld_color, ap_clouds);

    /* ---------------------------- Render Atmosphere --------------------------- */
    vec4 atmo_color = vec4(0.0);
    atmo_color += (enable_atm && enable_sun && enable_sun_as_light) ? vec4(atmo_raymarch(ray, sun, 1.0),1.0) : vec4(0.0);
    atmo_color += (enable_atm && enable_moon && enable_moon_as_light) ? vec4(atmo_raymarch(ray, moon, 0.000025),1.0) : vec4(0.0);    
    
    vec4 sun_color = (enable_sun) ? draw_sun(ray) : vec4(0.0);
    vec4 moon_color = (enable_moon) ? draw_moon(ray) : vec4(0.0);

    atmo_color += mix(sun_color, moon_color, moon_color.a);

    /* --------------------------------- Send it -------------------------------- */
    fragColor = vec4(mix(atmo_color, cld_color, cld_opacity).rgb,1.0);
}


