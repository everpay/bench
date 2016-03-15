from .common_site_config import get_config
import re, os, subprocess, urlparse
import bench

def generate_config(bench_path):
	config = get_config(bench_path)
	
	ports = {}
	for key in ('redis_cache', 'redis_queue', 'redis_socketio'):
		ports[key] = urlparse.urlparse(config[key]).port
	
	write_redis_config(
		template_name='redis_queue.conf',
		context={
			"port": ports['redis_queue'],
			"bench_path": os.path.abspath(bench_path),
		},
		bench_path=bench_path
	)

	write_redis_config(
		template_name='redis_socketio.conf',
		context={
			"port": ports['redis_socketio'],
		},
		bench_path=bench_path
	)
	
	write_redis_config(
		template_name='redis_cache.conf',
		context={
			"maxmemory": config.get('cache_maxmemory', '50'),
			"port": ports['redis_cache'],
			"redis_version": get_redis_version(),
		},
		bench_path=bench_path
	)

def write_redis_config(template_name, context, bench_path):
	template = bench.env.get_template(template_name)

	if "pid_path" not in context:
		context["pid_path"] = os.path.abspath(os.path.join(bench_path, "config", "pids"))

	with open(os.path.join(bench_path, 'config', template_name), 'w') as f:
		f.write(template.render(**context))

def get_redis_version():
	version_string = subprocess.check_output('redis-server --version', shell=True).strip()
	if re.search("Redis server version 2.4", version_string):
		return "2.4"
	if re.search("Redis server v=2.6", version_string):
		return "2.6"
	if re.search("Redis server v=2.8", version_string):
		return "2.8"
