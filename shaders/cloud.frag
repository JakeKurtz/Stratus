out vec4 fragColor;

uniform mat4 inv_vp_mat;
uniform vec2 img_size;
uniform float time;

uniform float altitude;

uniform bool enable_cld;
uniform bool enable_atmo;

uniform float attinuation_clamp;

uniform vec3 planet_center;
uniform float planet_radius;

uniform float atmo_radius;

uniform float scale_height_rayleigh;
uniform float scale_height_mie;
uniform float scale_height_absorption;

uniform float ray_intensity;
uniform float mie_intensity;
uniform float absorption_intensity;

uniform vec3 cld_center;
uniform float cld_radius;
uniform float cld_thickness;

uniform float cld_top_roundness;
uniform float cld_btm_roundness;

uniform float cld_density;
uniform float cld_top_density;
uniform float cld_btm_density;

uniform float cld_detail_scale;
uniform float cld_shape_scale;
uniform float cld_shape_scale2;
uniform float cld_coverage_scale;

uniform float cld_detail_intsty;
uniform float cld_shape_intsty;
uniform float cld_coverage_intsty;

uniform float cld_silver_intsty;
uniform float cld_silver_spread;
uniform float g;

uniform vec3 light_dir;
uniform float light_intsty;
uniform float sun_size;

uniform sampler3D noise_tex_3D_32;
uniform sampler3D noise_tex_3D_128;
uniform sampler2D noise_tex_2D_1024;
uniform sampler2D blue_noise;

float bn;
float light_intsty2 = 561.0;

#define PI          3.1415926535897932
#define M_3_16PI    0.0596831036594607 // 3 / (16pi)
#define M_1_4PI     0.0795774715459476 // 1 / (4pi)

#define MAX_CLOUD_STEPS 256
#define MAX_LIGHT_STEPS 128

#define MAX_VIEW_SAMPLES 64
#define MAX_LIGHT_SAMPLES 16

float atmo_depth;
float cld_depth;

// Scattering coefficients
vec3 beta_mie = vec3(21e-6) * mie_intensity;
vec3 beta_ozone = vec3(2.0556e-6, 4.9788e-6, 2.136e-7) * absorption_intensity;
vec3 beta_ray = vec3(5.87901e-6, 13.7369e-6, 33.5374e-6) * ray_intensity;

struct Ray
{
    vec3 o;
    vec3 d;
};

float saturate(float x)
{
    return clamp(x, 0.0, 1.0);
}

float remap(float x, float low1, float high1, float low2, float high2)
{
    return low2 + (x - low1) * (high2 - low2) / (high1 - low1);
}

vec3 tex_3d_pos(vec3 p) {
    vec3 p2;
    p2.x = mod(p.x, 1.0);
    p2.y = mod(p.y, 1.0);
    p2.z = mod(p.z, 1.0);
    return p2;
}

// ------------------------------------------------------------ //
//                      Phase Functions                         //
// ------------------------------------------------------------ //

float hg_phase(float g, vec3 wi, vec3 wo) 
{
    float theta = dot(wi, wo);
    float g2 = g*g;
    return M_1_4PI * ((1.0 - g2)/pow((1.0 + g2-(2.0*g*theta)), 1.5));
} 

float rayleigh_phase(vec3 wi, vec3 wo) 
{
    float theta = dot(wi, wo);
    return M_3_16PI * (1.0 + (theta*theta));
}

// ------------------------------------------------------------ //
// SDF Primitive Combinations
// source: https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm
// ------------------------------------------------------------ //

float sdf_sphere( vec3 p, float s ) 
{
  return length(p)-s;
}

float sdf_op_union(float d1, float d2) 
{ 
    return min(d1,d2); 
}

float sdf_op_sub(float d1, float d2) 
{ 
    return max(-d1,d2); 
}

float sdf_op_inter(float d1, float d2) 
{
    return max(d1,d2); 
}

float sdf_op_smooth_union(float d1, float d2, float k) 
{
    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix(d2, d1, h) - k*h*(1.0-h); 
}

float sdf_op_smooth_sub(float d1, float d2, float k) 
{
    float h = clamp(0.5 - 0.5*(d2+d1)/k, 0.0, 1.0);
    return mix(d2, -d1, h) + k*h*(1.0-h); 
}


float sdf_op_smooth_inter(float d1, float d2, float k) 
{
    float h = clamp(0.5 - 0.5*(d2-d1)/k, 0.0, 1.0);
    return mix(d2, d1, h) + k*h*(1.0-h); 
}

bool plane_intersect(vec3 norm, vec3 center, Ray ray, out float t)
{
    // assuming vectors are all normalized
    float denom = dot(norm, ray.d);
    if (denom > 1e-6) {
        vec3 p0l0 = center - ray.o;
        t = dot(p0l0, norm) / denom; 
        return (t >= 0);
    }
    return false;
}

bool disk_intersect(vec3 norm, vec3 center, float radius, Ray ray, out float t)
{
    if (plane_intersect(norm, center, ray, t)) {
        vec3 p = ray.o + ray.d * t;
        vec3 v = p - center;
        float d2 = dot(v, v);
        return (sqrt(d2) <= radius);
        // or you can use the following optimization (and precompute radius^2)
        // return d2 <= radius2; // where radius2 = radius * radius
     }
     return false;
}

bool solve_quadratic(float a, float b, float c, float d, out float t0, out float t1) 
{
    if (d > 0.0) {
        t0 = max((-b - sqrt(d)) / (2.0 * a), 0.0);
        t1 = (-b + sqrt(d)) / (2.0 * a);
        return true;
    } else {
        t0 = 1e32;
        t1 = 0;
        return false;
    }
}

bool sphere_intersect(Ray ray, vec3 center, float radius, out float t0, out float t1)
{
    vec3 L = ray.o - center;
    
    float a = dot(ray.d, ray.d);
    float b = 2.0 * dot(ray.d, L);
    float c = dot(L, L) - (radius * radius);
    float d = (b * b) - 4.0 * a * c;

    return solve_quadratic(a, b, c, d, t0, t1);
}

void shell_intersection(Ray ray, vec3 center, float outer_radius, float inner_radius, out float dist_to_start, out float dist_to_march) 
{
    dist_to_start = 0.0;
    dist_to_march = 0.0;

    if (outer_radius > inner_radius) {
        float t0, t1;
        bool hit_outer = sphere_intersect(ray, center, outer_radius, t0, t1);

        float s0, s1;
        bool hit_inner = sphere_intersect(ray, center, inner_radius, s0, s1);

        if (hit_outer) {
            if (t0 > 0 && t1 > 0) {
                dist_to_start = t0;
                dist_to_march = (hit_inner) ? s0 - t0 : t1 - t0;
            }
            else if (t0 <= 0 && t1 > 0) {
                dist_to_start = 0.0;
                if (hit_inner) dist_to_march = (s0 > 0) ? s0 : t1;
                else dist_to_march = t1;
            }
        }
    }
}

void atmo_intersect(Ray ray, out float dist_inside, out float dist_to) {

    float t0, t1;
	sphere_intersect(ray, planet_center, atmo_radius, t0, t1);
    if (t1 > 0) t1 -= t0;

    float s0, s1;
	sphere_intersect(ray, planet_center, planet_radius, s0, s1);
    if (s1 > 0) s1 -= s0;

	if (s1 < 0) {
		s0 = 1e32;
		s1 = 0;
	}

	dist_inside = min(t1, s0 - t0);
    dist_to = t0;
}

// ------------------------------------------------------------ //
//              Volumetric Atmosphere Methods                   //
// ------------------------------------------------------------ //

float atmo_density(vec3 pos, float scale_height) 
{
    vec3 q = planet_center + normalize(pos - planet_center) * planet_radius;
    float height = distance(pos, q);
    return exp(-height / scale_height);
}

void atmo_light(Ray ray, float ray_length, out float light_optical_depth_ray, out float light_optical_depth_mie, out float light_optical_depth_absorp) 
{
	float step_size = ray_length / float(MAX_LIGHT_SAMPLES);
    //ray.o += (bn*step_size*0.1) * ray.d;
	light_optical_depth_ray = 0.0;
	light_optical_depth_mie = 0.0;
    light_optical_depth_absorp = 0.0;

	for (float march_pos = 0.0; march_pos < ray_length; march_pos += step_size) 
    {
		vec3 density_sample_point = ray.o + ray.d * (march_pos + 0.5 * step_size);

		float density_ray = atmo_density(density_sample_point, scale_height_rayleigh) * step_size;
		float density_mie = atmo_density(density_sample_point, scale_height_mie) * step_size;
        float density_absorp = atmo_density(density_sample_point, scale_height_absorption) * step_size;

		light_optical_depth_ray += density_ray;
		light_optical_depth_mie += density_mie;
        light_optical_depth_absorp += density_absorp;
	}
}

void light_ray_vis(Ray ray, out float visible, out float march_length) 
{
    march_length = 0.0;
    visible = 0.0;

    if (atmo_radius > planet_radius) {
        float t0, t1;
        bool hit_outer = sphere_intersect(ray, planet_center, atmo_radius, t0, t1);

        float s0, s1;
        bool hit_inner = sphere_intersect(ray, planet_center, planet_radius, s0, s1);

        bool atmo_grazed = (t0 == t1);
        bool atmo_behind = (t0 <= 0 && t1 <= 0);
        bool atmo_inside = (t0 <= 0 && t1 > 0);
        bool atmo_front = (t0 > 0 && t1 > 0);

        bool plnt_grazed = (s0 == s1);
        bool plnt_behind = (s0 <= 0 && s1 <= 0);
        bool plnt_inside = (s0 <= 0 && s1 > 0);
        bool plnt_front = (s0 > 0 && s1 >= 0);

        if (hit_outer) {
            if (atmo_grazed || atmo_behind) {
                visible = 0.0;
                march_length = 0.0;
            } else if (atmo_inside || atmo_front) {
                if (hit_inner) {
                    if (plnt_grazed || plnt_behind) {
                        march_length = t1;
                        visible = 1.0;
                    } else if (plnt_inside) {
                        march_length = 0.0;
                        visible = 0.0;
                    } else if (plnt_front) {
                        march_length = 0.0;
                        visible = 0.0;
                    }
                } else {
                    march_length = t1;
                    visible = 1.0;
                }
            }
        }
    }
}

vec3 direct_light_color(Ray ray) {
    float dist_to_march, light_visible;
    light_ray_vis(ray, light_visible, dist_to_march);

    float light_optical_depth_ray, light_optical_depth_mie, light_optical_depth_absorp;
    atmo_light(ray, dist_to_march, light_optical_depth_ray, light_optical_depth_mie, light_optical_depth_absorp);

    float density_ray = atmo_density(ray.o, scale_height_rayleigh);
    float density_mie = atmo_density(ray.o, scale_height_mie);
    float density_absorp = atmo_density(ray.o, scale_height_absorption);

    vec3 out_scatter = exp(-light_optical_depth_mie*vec3(2e-6) * 5.0)*exp(-light_optical_depth_ray*beta_ray)*exp(-light_optical_depth_absorp*beta_ozone);

    vec3 color = out_scatter * light_visible;

    return color;
}

vec3 get_transmittance(Ray ray, float view_optical_depth_ray, float view_optical_depth_mie)
{
        float dist_to_march, light_visible;
        light_ray_vis(ray, light_visible, dist_to_march);

		float light_optical_depth_ray, light_optical_depth_mie, light_optical_depth_absorp;
		atmo_light(ray, dist_to_march, light_optical_depth_ray, light_optical_depth_mie, light_optical_depth_absorp);

		return exp( -(beta_ray*(light_optical_depth_ray + view_optical_depth_ray) +
                      beta_mie*(light_optical_depth_mie + view_optical_depth_mie) + 
                      beta_ozone*(light_optical_depth_absorp + view_optical_depth_ray))) * (light_visible);
}

vec3 atmo_raymarch(Ray ray, float ray_length, out vec3 opacity) 
{
	float step_size = ray_length / float(MAX_VIEW_SAMPLES);

	float phase_ray = rayleigh_phase(light_dir, ray.d);
	float phase_mie = hg_phase(0.7, light_dir, ray.d);

	float view_optical_depth_ray = 0.0;
	float view_optical_depth_mie = 0.0;

	vec3 in_scatter_ray = vec3(0);
	vec3 in_scatter_mie = vec3(0);

    float dst_to_start, dst_to_march;
    shell_intersection(ray, cld_center, cld_radius+cld_thickness, cld_radius, dst_to_start, dst_to_march);

    //ray.o += (bn*step_size*0.1) * ray.d;

    float foo = saturate(remap(ray_length, cld_depth, atmo_depth, 0.0, 1.0));

    for (float march_pos = 0.0; march_pos < ray_length; march_pos += step_size) {
		vec3 current_pos = ray.o + ray.d * (march_pos + 0.5 * step_size);

		float density_ray = atmo_density(current_pos, scale_height_rayleigh) * step_size;
		float density_mie = atmo_density(current_pos, scale_height_mie) * step_size;

        Ray light_ray;
        light_ray.o = current_pos;
        light_ray.d = light_dir;

        vec3 transmittance = get_transmittance(light_ray, view_optical_depth_ray, view_optical_depth_mie);

		view_optical_depth_ray += density_ray;
		view_optical_depth_mie += density_mie;

		in_scatter_ray += density_ray * transmittance;
		in_scatter_mie += density_mie * transmittance;
	}
	return ((in_scatter_ray * beta_ray * phase_ray) + (in_scatter_mie * (mix(vec3(0.0), beta_mie, foo)) * phase_mie)) * (light_intsty);
}

bool cloud_density(vec3 p, out float density, out float dist) 
{
    // translate cloud shell
    p -= cld_center;
/*
    vec3 d2 = normalize(p-cld_center);
    vec3 min_point = d2 * cld_radius;
    vec3 max_point = d2 * (cld_radius + cld_thickness);

    float p_h = remap(p.z, min_point.z, max_point.z, 0.0, 1.0);
    */

    vec3 d = normalize(p);
    float min_height = (d*cld_radius).z;
    float max_height = (d*(cld_radius + cld_thickness)).z;

    float p_h = remap(p.z, min_height, max_height, 0.0, 1.0);

    float wh = texture(noise_tex_3D_128, tex_3d_pos(p * cld_shape_scale2)).b;

    float SR_b = saturate(remap(p_h, 0.0, cld_btm_roundness, 0.0, 1.0));
    float SR_t = saturate(remap(p_h, wh*cld_top_roundness, wh, 1.0, 0.0));
    
    float DR_b = saturate(remap(p_h, 0.0, cld_btm_density, 0.0, 1.0));
    float DR_t = saturate(remap(p_h, cld_top_density, 1.0, 1.0, 0.0));
        
    float SA = SR_b * SR_t;
    float DA = DR_b * DR_t;
  
    float inner_shell = sdf_sphere(p, cld_radius);
    float outer_shell = sdf_sphere(p, cld_radius + cld_thickness);
    float cld_shell = sdf_op_sub(inner_shell, outer_shell);

    if (cld_shell < 0.0 && p.z > (-cld_center.z-altitude)) {

        vec4 cns =  texture(noise_tex_2D_1024, (p.xy + time * 20) * cld_coverage_scale);
        vec4 sns =  texture(noise_tex_3D_128, tex_3d_pos((p + time * 5) * cld_shape_scale));
        vec4 dns =  texture(noise_tex_3D_32, tex_3d_pos((p + time * 5) * cld_detail_scale));

        float DN = dns.r*0.625+dns.g*0.25+dns.b*0.125;
        float SN = sns.g*0.625+sns.b*0.25+sns.a*0.125;

        float cld_coverage = remap(cns.x * cld_coverage_intsty, 0.0, 1.0, -1.0, 1.0) * SA;
        float cld_shape = remap(sns.r, SN - 1.0, 1, 0.0, 1.0) * cld_shape_intsty;
        float cld_detail = 0.35 * mix(DN, 1.0 - DN, saturate(p_h * 5.0)) * cld_detail_intsty;

        cld_shell = sdf_op_sub(cld_coverage, cld_shell);
        cld_shell = (cld_detail) + cld_shape + cld_shell;
        
        if (cld_shell < 0.f) {
            float sdfMultiplier = min(abs(cld_shell)*attinuation_clamp, 1.0) * DA;
            density = sdfMultiplier;
            dist = cld_shell;
            return true;
        } else {
            density = 0.0;
            dist = cld_shell;
            return false;
        }
    } else {
        density = 0.0;
        return false;
    }   
}

vec3 cloud_ray_light(Ray ray) 
{
    Ray light_ray;
    light_ray.o = ray.o;
    light_ray.d = light_dir;
    vec3 light_color = direct_light_color(light_ray)*light_intsty;
    
    float phase_mie = max(hg_phase(g, light_dir, ray.d), cld_silver_intsty * hg_phase(0.99-cld_silver_spread, light_dir, ray.d));

    float extinction_coeff = 0.5;
    float scattering_coeff = 0.5;

    float total_density = 0.0;

    float dst_to_start, dst_to_march;
    shell_intersection(ray, cld_center, cld_radius+cld_thickness, cld_radius, dst_to_start, dst_to_march);

    float step_size_orig = dst_to_march / float(MAX_LIGHT_STEPS);
    float step_size = step_size_orig;

    light_ray.o = ray.o;
    vec3 ray_start_pos = (light_ray.o + light_dir * dst_to_start);

    ray_start_pos += (bn * step_size * 2) * ray.d;

    for (float march_dst = 0.0; march_dst < dst_to_march; march_dst += step_size)
    {
        light_ray.o = ray_start_pos + march_dst * light_dir;

        float ds, dist;
        bool in_cloud = cloud_density(light_ray.o, ds, dist);
        if (in_cloud) {
            total_density += ds * step_size * cld_density;
        }

        //step_size = step_size_orig * 1.0/pow(max(0.4, -ds),0.8); 
        //total_dist += in_cloud ? step_size : max(dist, step_size);
        //current_pos = ray.o + (total_dist*light_dir);
    }

    float beer = exp(-total_density*extinction_coeff);
    float powder = 1.0 - exp(-total_density*extinction_coeff*1.5);

    vec3 light = vec3(0.0);

    for (int i = 0; i < 8; i++){
        light += pow(0.5,i)*scattering_coeff*exp(-total_density*pow(0.5,i)) * light_color * max(hg_phase(g*pow(0.5,i), light_dir, ray.d), cld_silver_intsty * hg_phase((0.99-cld_silver_spread)*pow(0.5,i), light_dir, ray.d));
    }

    return light;// + vec3(0.01,0.02,0.03);
}

vec3 cloud_raymarch(Ray ray, out float depth, out float opacity) 
{
    depth = 0.0;
    opacity = 0.0;

    float depth_count = 0.0;
    vec3 color = vec3(0.0);

    bool exit = false;

    float transmittance = 1.0;
    vec4 scatter_trans = vec4(0.0, 0.0, 0.0, 1.0);

    float extinction_coeff = 0.5;
    float scattering_coeff = 0.5;
    float absorption_coeff = 0.5;

    float dst_to_start, dst_to_march;
    shell_intersection(ray, cld_center, cld_radius+cld_thickness, cld_radius, dst_to_start, dst_to_march);

    float step_size_orig = dst_to_march / float(MAX_CLOUD_STEPS);
    float step_size = step_size_orig;

    vec3 ray_start_pos = (ray.o + ray.d * dst_to_start);
    ray_start_pos += (bn * step_size * 4)*ray.d;

    for (float march_dst = 0.0; march_dst < dst_to_march; march_dst += step_size)
    {
        ray.o = ray_start_pos + march_dst * ray.d;

        if (scatter_trans.a < 1e-10) {
            //step_size = ray_march_length - total_dist;
            exit = true;
        }

        float ds, dist;
        bool in_cloud = cloud_density(ray.o, ds, dist);
        if (in_cloud) 
        {
            ds *= cld_density * step_size;

            transmittance = exp(-ds * extinction_coeff);

            scatter_trans.a *= transmittance;
            scatter_trans.rgb += scatter_trans.a * ds * cloud_ray_light(ray);
            
            depth += (dst_to_start + march_dst) * scatter_trans.a;
            depth_count += scatter_trans.a;

        }
        
        if (exit) break;
        
        //step_size = step_size_orig * 1.0 / pow(max(0.4, -ds), 0.8); // increase step size based on density
        //total_dist += step_size;//in_cloud ? step_size : max(dist, step_size);
        //step_size = (ds > 0.0) ? step_size : max(100, step_size);
    }

    if (depth_count != 0.0) depth /= depth_count;
    
    //color = 1.0 - exp(-scatter_trans.rgb);

    opacity = 1.0 - scatter_trans.a;

    return scatter_trans.rgb;
}

float linearize_depth(float d,float zNear,float zFar) {
    return zNear * zFar / (zFar + d * (zNear - zFar));
}

vec3 sunWithBloom(vec3 rayDir, vec3 sunDir, float sun_size) {
    const float sunSolidAngle = sun_size*PI/180.0;
    const float minSunCosTheta = cos(sunSolidAngle);

    float cosTheta = dot(rayDir, sunDir);
    if (cosTheta >= minSunCosTheta) return vec3(1.0);
    
    float offset = minSunCosTheta - cosTheta;

    float gaussianBloom = exp(-offset*50000.0)*.5;
    float invBloom = 1.0/(0.02 + offset*300.0)*0.01;
    return vec3(gaussianBloom);
}
/*
void main()
{   
    vec2 p_NDC; // [-1, 1] x [-1, 1]
    p_NDC.x = 2.0 * ((gl_FragCoord.x + 0.5) / img_size.x) - 1.0;
    p_NDC.y = 2.0 * ((gl_FragCoord.y + 0.5) / img_size.y) - 1.0;

    vec4 p_near_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, -1.0, 1.0);
    vec4 p_far_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, 1.0, 1.0);

    vec3 p_near = vec3(p_near_NDC.xyz) / p_near_NDC.w;
    vec3 p_far = vec3(p_far_NDC.xyz) / p_far_NDC.w;

    vec2 uv = gl_FragCoord.xy / img_size.xy;

    //float xy = texture(blue_noise, uv).r;
    //vec4 noise_test = texture(blue_noise, uv*1);

    bn = texture(blue_noise, uv*16).r;
    //bn = fract(bn * 0.61803398875);

    Ray ray;
    ray.o = vec3(0.0);
    ray.d = normalize(p_far - p_near);

    float dst_to_atmo;
    atmo_intersect(ray, atmo_depth, dst_to_atmo);

    float cld_opacity;
    vec4 cld_color = enable_cld ? vec4(cloud_raymarch(ray, cld_depth, cld_opacity), 1.0) : vec4(0.0);

    Ray atmo_ray;
    atmo_ray.o = ray.o + ray.d * dst_to_atmo;
    atmo_ray.d = ray.d; 

    float depth = mix(cld_depth, atmo_depth, (1.0 - cld_opacity));  

    depth = min(atmo_depth, (depth == 0.0) ? 1e32 : depth);

    //float world_depth = linearize_depth(texture(depth_tex, uv).r, 0.1, 5000);
    //vec4 test = texture(depth_tex, uv);

    //depth = min(depth, world_depth);

    vec3 atmo_opacity = vec3(1.0);   
    vec4 atmo_color = enable_atmo ? vec4(atmo_raymarch(atmo_ray, depth, atmo_opacity),1.0) : vec4(0.0);
*/
    /*vec4 sun_color = vec4(0.0,0.0,0.0,1.0);
    float t;
    if (disk_intersect(light_dir, 2.0*light_dir, sun_size, ray, t))
    {
        atmo_color = vec4(direct_light_color(ray) * light_intsty, 1.0);
    }
    */
/*
    atmo_color += vec4(sunWithBloom(ray.d, light_dir, sun_size)* direct_light_color(ray) * light_intsty, 1.0);

    fragColor = mix(cld_color, atmo_color, remap(depth, cld_depth, atmo_depth, 0.0, 1.0));
    //fragColor.a *= world_depth;
}
*/

void main()
{   
    vec2 p_NDC; // [-1, 1] x [-1, 1]
    p_NDC.x = 2.0 * ((gl_FragCoord.x + 0.5) / img_size.x) - 1.0;
    p_NDC.y = 2.0 * ((gl_FragCoord.y + 0.5) / img_size.y) - 1.0;

    vec4 p_near_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, -1.0, 1.0);
    vec4 p_far_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, 1.0, 1.0);

    vec3 p_near = vec3(p_near_NDC.xyz) / p_near_NDC.w;
    vec3 p_far = vec3(p_far_NDC.xyz) / p_far_NDC.w;

    vec2 uv = gl_FragCoord.xy / img_size.xy;   

    Ray ray;
    ray.o = vec3(0.0);
    ray.d = normalize(p_far - p_near);
    
    float c =  mod( ( uv.x * 64.0), 1.0);
    float v =  mod( ( uv.y * 64.0), 1.0);

    bn = texture(blue_noise, vec2(c,v)).r;

    float dst_to_atmo;
    atmo_intersect(ray, atmo_depth, dst_to_atmo);

    float cld_opacity;
    vec4 cld_color = enable_cld ? vec4(cloud_raymarch(ray, cld_depth, cld_opacity), 1.0) : vec4(0.0);

    Ray atmo_ray;
    atmo_ray.o = ray.o + ray.d * dst_to_atmo;
    atmo_ray.d = ray.d;

    float depth = mix(cld_depth, atmo_depth, (1.0 - cld_opacity));
    depth = min(atmo_depth, (depth == 0.0) ? 1e32 : depth);

    vec3 atmo_opacity = vec3(1.0);   
    vec4 atmo_color = enable_atmo ? vec4(atmo_raymarch(atmo_ray, depth, atmo_opacity),1.0) : vec4(0.0);

    atmo_color += vec4(sunWithBloom(ray.d, light_dir, sun_size)* direct_light_color(ray) * light_intsty, 1.0);

    fragColor = vec4(mix(cld_color.rgb, atmo_color.rgb, remap(depth, cld_depth, atmo_depth, 0.0, 1.0)), 1.0);
}