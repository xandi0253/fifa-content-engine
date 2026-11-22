extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene = load("res://campo.tscn").instantiate()
	root.add_child(scene)
	scene.set_process(false)
	for i in 120:
		scene.time = i/24.0
		scene.update_scene()
		var support: Vector3 = scene.athlete_parts["Lboot"].position
		if support.distance_to(scene.PLANT+Vector3(0,-.025,-.065))>.00001:
			push_error("O pé de apoio se deslocou")
			quit(1)
			return
		var p: Vector3 = scene.ball.position
		scene.behind = not scene.behind
		scene.update_scene()
		if scene.ball.position.distance_to(p)>.00001:
			push_error("A câmera alterou a trajetória")
			quit(1)
			return
	scene.time = scene.HIT
	scene.update_scene()
	var toe: Vector3 = scene.athlete_parts["Rboot"].position+Vector3.FORWARD*.135
	if absf(toe.distance_to(scene.ball.position)-scene.BALL_RADIUS)>.015:
		push_error("O contato entre bola e chuteira ficou fora da tolerância")
		quit(1)
		return
	print("120 quadros verificados: apoio, duas câmeras e contato a 2 segundos.")
	quit()
