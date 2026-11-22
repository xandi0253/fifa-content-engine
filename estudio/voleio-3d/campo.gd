extends Node3D

const HIT := 2.0
const DURATION := 5.0
const PLANT := Vector3(-0.14, 0.095, 0.12)
const BALL_RADIUS := 0.11
const TEAL := Color("#15938d")
const NAVY := Color("#18283e")
const SKIN := Color("#aa704d")
const GOLD := Color("#eeb44c")
const WHITE := Color("#e7e6cb")
const STRIKE_KEYS := [
	[0.0, Vector3(.18,.095,.12)], [.75, Vector3(.18,.095,.12)],
	[1.28, Vector3(.24,.27,.41)], [1.66, Vector3(.27,.59,.53)],
	[1.88, Vector3(.29,.51,.15)], [HIT, Vector3(.32,.51,-.52)],
	[2.18, Vector3(.36,.66,-.63)], [2.5, Vector3(.39,.38,-.48)],
	[2.86, Vector3(.32,.095,-.41)], [DURATION, Vector3(.32,.095,-.41)]]
var body := Node3D.new()
var athlete_parts := {}
var materials := {}
var ball := Node3D.new()
var camera := Camera3D.new()
var stats := Label.new()
var profile := 1
var behind := false
var paused := false
var time := 0.0
var export_mode := false
var samples: Array[float] = []
var previous_us := 0

func surface(color: Color) -> StandardMaterial3D:
	if not materials.has(color):
		var m := StandardMaterial3D.new()
		m.albedo_color = color
		m.roughness = .86
		materials[color] = m
	return materials[color]

func piece(parent: Node3D, mesh: Mesh, at: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var obj := MeshInstance3D.new()
	obj.mesh = mesh
	obj.material_override = surface(color)
	parent.add_child(obj)
	obj.position = at
	obj.scale = size
	return obj

func oval(parent: Node3D, at: Vector3, size: Vector3, color: Color) -> MeshInstance3D:
	var mesh := SphereMesh.new()
	mesh.radial_segments = 16
	mesh.rings = 8
	return piece(parent, mesh, at, size, color)

func box(at: Vector3, size: Vector3, color: Color) -> void:
	piece(self, BoxMesh.new(), at, size, color)

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	export_mode = "--filme" in args
	behind = "--gol" in args
	add_child(body)
	add_child(ball)
	add_child(camera)
	camera.current = true
	var sun := DirectionalLight3D.new()
	add_child(sun)
	sun.rotation_degrees = Vector3(-50,-30,0)
	sun.light_energy = 1.2
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("#738da1")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("#ffe6c9")
	env.ambient_light_energy = .75
	get_viewport().world_3d.environment = env
	for i in 14:
		box(Vector3(0,-.06,-15+i*2.0),Vector3(30,.1,2), Color("#41765d") if i%2 else Color("#468069"))
	box(Vector3(0,.007,-5.85),Vector3(14,.01,.045),WHITE)
	for side in [-1,1]:
		box(Vector3(side*2.3,1,-6),Vector3(.07,2,.07),WHITE)
	box(Vector3(0,2,-6),Vector3(4.67,.07,.07),WHITE)
	for i in 24:
		box(Vector3(-2.3+i*.20,1,-6.33),Vector3(.009,2,.009),Color("#a6b7ae"))
	for i in 11:
		box(Vector3(0,i*.2,-6.33),Vector3(4.6,.009,.009),Color("#a6b7ae"))
	for i in 4:
		box(Vector3(0,i*.45,-9-i*.8),Vector3(23,.5,.9),Color("#384b59"))
	for i in 2:
		var z := -4.5+i*10.
		box(Vector3(-10,2,z),Vector3(.12,4,.12),NAVY)
		box(Vector3(-10,4,z),Vector3(.24,.3,1.2),WHITE)
	oval(body,Vector3(0,.22,0),Vector3(.46,.57,.28),TEAL)
	oval(body,Vector3(0,-.015,0),Vector3(.37,.22,.25),NAVY)
	oval(body,Vector3(0,.63,-.025),Vector3(.25,.32,.24),SKIN)
	oval(body,Vector3(0,.731,-.013),Vector3(.265,.18,.25),NAVY)
	for side in [-1,1]:
		oval(body,Vector3(side*.055,.647,-.139),Vector3(.024,.026,.013),NAVY)
	for side in [-1,1]:
		var bib := Label3D.new()
		body.add_child(bib)
		bib.text = "9"
		bib.font_size = 64
		bib.pixel_size = .0027
		bib.outline_size = 0
		bib.position = Vector3(0,.24,side*.144)
		bib.rotation.y = PI if side==-1 else 0.
	for id in ["L","R"]:
		for seg in ["thigh","shin","sleeve","arm","boot"]:
			var tint: Color = {"thigh":NAVY,"shin":WHITE,"sleeve":TEAL,"arm":SKIN,"boot":GOLD}[seg]
			athlete_parts[id+seg] = oval(self,Vector3.ZERO,Vector3.ONE,tint)
	oval(ball,Vector3.ZERO,Vector3.ONE*BALL_RADIUS*2,WHITE)
	for dir in [Vector3.UP,Vector3.DOWN,Vector3.RIGHT,Vector3.LEFT,Vector3.FORWARD,Vector3.BACK]:
		oval(ball,dir*.091,Vector3.ONE*.057,NAVY)
	var layer := CanvasLayer.new()
	add_child(layer)
	layer.add_child(stats)
	stats.position = Vector2(16,12)
	stats.add_theme_constant_override("outline_size",5)
	stats.visible = not export_mode
	get_viewport().scaling_3d_scale = 1.0 if export_mode else .75
	update_scene()
	update_stats()

func foot(t: float) -> Vector3:
	for i in range(1,STRIKE_KEYS.size()):
		var a: Array = STRIKE_KEYS[i-1]
		var b: Array = STRIKE_KEYS[i]
		if t <= b[0]:
			var u := smoothstep(float(a[0]),float(b[0]),t)
			return (a[1] as Vector3).lerp(b[1],u)
	return STRIKE_KEYS.back()[1]

func ball_path(t: float) -> Vector3:
	var contact := foot(HIT)+Vector3(0,-.025,-.30)
	if t<HIT:
		var u := t/HIT
		return Vector3(-3.2,1.62,-1.3).lerp(contact,u)+Vector3.UP*.55*4*u*(1-u)
	var u := clampf((t-HIT)/.56,0,1)
	var goal := Vector3(.78,1.35,-6.24)
	if u<1:
		return contact.lerp(goal,u)+Vector3.UP*.18*4*u*(1-u)
	var v := clampf((t-HIT-.56)/.84,0,1)
	return goal.lerp(Vector3(.85,.12,-5.98),v*v)+Vector3.UP*.09*absf(sin(v*PI*2))*(1-v)

func segment(key: String, a: Vector3, b: Vector3, width: float) -> void:
	var obj: MeshInstance3D = athlete_parts[key]
	var y := (b-a).normalized()
	var axis := Vector3.RIGHT if absf(y.x)<.9 else Vector3.FORWARD
	var z := axis.cross(y).normalized()
	obj.transform = Transform3D(Basis(y.cross(z)*width,y*(a.distance_to(b)+.035),z*width),(a+b)*.5)

func leg(id: String, hip: Vector3, ankle: Vector3) -> void:
	var delta := ankle-hip
	var pole := Vector3.FORWARD
	var forward := (pole-delta.normalized()*pole.dot(delta.normalized())).normalized()
	var knee := (ankle+hip)*.5+forward*sqrt(maxf(0,.47*.47-delta.length_squared()*.25))
	segment(id+"thigh",hip,knee,.17)
	segment(id+"shin",knee,ankle,.105)
	var boot: MeshInstance3D = athlete_parts[id+"boot"]
	boot.position = ankle+Vector3(0,-.025,-.065)
	boot.scale = Vector3(.13,.12,.27)

func update_scene() -> void:
	var windup := smoothstep(.75,1.67,time)*(1.-smoothstep(1.75,2.14,time))
	var follow := smoothstep(1.77,2.17,time)*(1.-smoothstep(2.42,3.35,time))
	var settle := smoothstep(2.25,3.45,time)
	body.position = Vector3(.035*follow,.955-.065*windup-.035*follow,-.10*follow-.14*settle)
	body.rotation = Vector3(.1*windup-.12*follow,.58*windup-.73*follow,-.16*windup+.23*follow)
	leg("L",body.to_global(Vector3(-.105,0,0)),PLANT)
	leg("R",body.to_global(Vector3(.105,0,0)),foot(time))
	for side in [-1,1]:
		var id := "L" if side==-1 else "R"
		var shoulder := body.to_global(Vector3(side*.17,.397,0))
		var elbow := shoulder+Vector3(side*(.15+.13*windup+.06*follow),-.23+.13*follow,side*(windup-follow)*.20)
		var hand := elbow+Vector3(side*.07,-.12+.09*windup,-.18)
		segment(id+"sleeve",shoulder,elbow,.12)
		segment(id+"arm",elbow,hand,.086)
	ball.position = ball_path(time)
	ball.rotation.x = -time*8
	camera.position = Vector3(1.6,1.36,-7.1) if behind else Vector3(3.65,1.22,1.65)
	camera.look_at(Vector3(.03,.93,-.45))
	camera.fov = 34 if behind else 39

func update_stats() -> void:
	var p95 := "medindo"
	if samples.size()>=24:
		var sorted := samples.duplicate()
		sorted.sort()
		p95 = "%.1f ms" % sorted[ceili(sorted.size()*.95)-1]
	stats.text = "Voleio 3D   |   %s   |   escala %d%%   |   %d FPS   |   P95 %s\nC câmera    Q qualidade    Espaço pausa    R reinicia" % [
		"atrás do gol" if behind else "lateral",roundi(get_viewport().scaling_3d_scale*100),Engine.get_frames_per_second(),p95]

func _process(delta: float) -> void:
	var now := Time.get_ticks_usec()
	if previous_us and not export_mode:
		samples.append((now-previous_us)/1000.)
		if samples.size()>240:
			samples.pop_front()
	previous_us = now
	if not paused:
		time = fmod(time+delta,DURATION)
		update_scene()
	if Engine.get_process_frames()%12==0 and not export_mode:
		update_stats()

func _unhandled_key_input(event: InputEvent) -> void:
	if export_mode or not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_C: behind = not behind
		KEY_R: time = 0.
		KEY_SPACE: paused = not paused
		KEY_Q:
			profile = (profile+1)%3
			get_viewport().scaling_3d_scale = [.5,.75,1.][profile]
			samples.clear()
	update_scene()
	update_stats()
