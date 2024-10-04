
DELIMITER 
--
-- Procedimientos
--
CREATE PROCEDURE `AddGestion` (IN `p_descripcion` TEXT, IN `p_nombre_gestion` VARCHAR(45), IN `p_id_person` INT)   BEGIN
    DECLARE v_id_gestion INT;

    -- Iniciar transacción
    START TRANSACTION;

    -- Insertar en la tabla gestion si es la primera empresa
    IF NOT EXISTS (SELECT 1 FROM gestion WHERE nombre_gestion = p_nombre_gestion AND descripcion = p_descripcion AND id_person = p_id_person) 
    THEN
        INSERT INTO gestion (descripcion, nombre_gestion, id_person)
        VALUES (p_descripcion, p_nombre_gestion, p_id_person);
        
        -- Obtener el ID de la gestión recién insertada
        SET v_id_gestion = (SELECT id_gestion FROM gestion WHERE nombre_gestion = p_nombre_gestion AND descripcion = p_descripcion AND id_person = p_id_person);
    ELSE
        -- Recuperar el ID de gestión si ya existe
        SELECT id_gestion INTO v_id_gestion FROM gestion WHERE nombre_gestion = p_nombre_gestion AND descripcion = p_descripcion AND id_person = p_id_person;
    END IF;

    -- Insertar en la tabla gestionar para relacionar la gestión con el gestor
    IF NOT EXISTS (SELECT 1 FROM gestionar WHERE id_person = p_id_person AND id_gestion = v_id_gestion) THEN
        INSERT INTO gestionar (id_person, id_gestion)
        VALUES (p_id_person, v_id_gestion);
    END IF;

    -- Confirmar la transacción
    COMMIT;

    -- Opcional: Devolver el id_gestion generado
    SELECT v_id_gestion AS id_gestion;

END

CREATE PROCEDURE `AddGestor` (IN `p_nombre` VARCHAR(50), IN `p_apellidos` VARCHAR(50), IN `p_dni` VARCHAR(50), IN `p_email` VARCHAR(100), IN `p_password` VARCHAR(100))   BEGIN
    DECLARE v_id_person INT;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        -- En caso de error, deshacer los cambios y lanzar una excepción personalizada
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ocurrió un error durante la transacción.';
    END;

    -- Iniciar transacción
    START TRANSACTION;

    -- Comprobar si ya existe una persona con el mismo DNI o email
    IF EXISTS (SELECT 1 FROM persona WHERE dni = p_dni OR email = p_email) THEN
        -- Obtener el id_person de la persona existente
        SELECT id_person INTO v_id_person 
        FROM persona 
        WHERE dni = p_dni OR email = p_email;

        -- Insertar en la tabla gestor
        INSERT INTO gestor (id_person, password)
        VALUES (v_id_person, p_password);
    ELSE
        -- Insertar en la tabla persona
        INSERT INTO persona (nombre, apellidos, dni, email)
        VALUES (p_nombre, p_apellidos, p_dni, p_email);

        SELECT id_person INTO v_id_person 
        FROM persona 
        WHERE dni = p_dni OR email = p_email;

        -- Insertar en la tabla gestor
        INSERT INTO gestor (id_person, password)
        VALUES (v_id_person, p_password);
    END IF;

    -- Confirmar la transacción
    COMMIT;

    -- Devolver el id_person generado o existente
    SELECT v_id_person AS id_person;
END

CREATE PROCEDURE `AddGestorGestionExistente` (IN `p_email` VARCHAR(100), IN `p_nombre` VARCHAR(50), IN `v_id_gestion` INT)   BEGIN
    DECLARE v_id_person INT;

    -- Seleccionar el id_person del gestor basado en el nombre y el email
    SELECT g.id_person INTO v_id_person
    FROM persona p
    JOIN gestor g ON p.id_person = g.id_person
    WHERE p.nombre = p_nombre AND p.email = p_email
    LIMIT 1;  -- Añadir un límite por seguridad, aunque se asume que nombre y email son únicos.

    -- Verificar si se encontró el gestor
    IF v_id_person IS NOT NULL THEN
        -- Insertar el gestor en la tabla gestionar para la gestión existente
        INSERT INTO gestionar (id_person, id_gestion) 
        VALUES (v_id_person, v_id_gestion);
    ELSE
        -- Lanzar un error si no se encontró el gestor
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se encontró el gestor';
    END IF;
END

CREATE PROCEDURE `AddUsuario` (IN `p_nombre` VARCHAR(50), IN `p_apellidos` VARCHAR(50), IN `p_dni` VARCHAR(50), IN `p_email` VARCHAR(100), IN `u_nombre_usuario` VARCHAR(45))   BEGIN
    DECLARE v_id_person INT;

    -- Iniciar transacción
    START TRANSACTION;

    -- Comprobar si ya existe una persona con el mismo DNI y email
    SELECT id_person INTO v_id_person 
    FROM persona 
    WHERE dni = p_dni AND email = p_email
    LIMIT 1;

    -- Si no se encontró ninguna persona, insertar una nueva
    IF v_id_person IS NULL THEN
        INSERT INTO persona (nombre, apellidos, dni, email)
        VALUES (p_nombre, p_apellidos, p_dni, p_email);

        -- Obtener el id_person recién insertado
        SET v_id_person = (SELECT id_person FROM persona WHERE dni = p_dni AND email = p_email LIMIT 1);
    END IF;

    -- Insertar en la tabla usuario si no existe un usuario con ese id_person y nombre_usuario
    IF NOT EXISTS (
        SELECT 1 FROM usuario WHERE id_person = v_id_person AND nombre_usuario = u_nombre_usuario
    ) THEN
        INSERT INTO usuario (id_person, nombre_usuario)
        VALUES (v_id_person, u_nombre_usuario);
    END IF;
    
    SELECT v_id_person AS id_person;

    -- Confirmar la transacción
    COMMIT;
END

CREATE PROCEDURE `DeleteGestion` (IN `p_id_gestion` INT)   BEGIN
    -- Iniciar transacción
    START TRANSACTION;

    -- Eliminar registros de la tabla `gestionar` relacionados con la gestión
    DELETE FROM gestionar
    WHERE id_gestion = p_id_gestion;

    -- Eliminar registros de la tabla `gestionempresas` relacionados con la gestión
    DELETE FROM gestionempresas
    WHERE id_gestion = p_id_gestion;
    
    -- Eliminar el registro de la tabla `gestion` para la gestión dada
    DELETE FROM gestion
    WHERE id_gestion = p_id_gestion;

    -- Confirmar la transacción
    COMMIT;

    -- Opcional: Mensaje de éxito
    SELECT 'Gestión y registros relacionados eliminados exitosamente' AS Message;
    
END

CREATE PROCEDURE `GetGestionesPorGestor` (IN `p_id_person` INT)   BEGIN
    -- Seleccionar los nombres de las gestiones asociadas al id_person proporcionado
    SELECT g.nombre_gestion, g.descripcion, g.id_gestion
    FROM gestionar ge
    JOIN gestion g ON ge.id_gestion = g.id_gestion
    WHERE ge.id_person = p_id_person;
END

CREATE PROCEDURE `GetNombreGestionPorID` (IN `p_id_gestion` INT)   BEGIN
    -- Seleccionar el nombre de la gestión asociada al id_gestion proporcionado
    SELECT g.nombre_gestion
    FROM gestionar ge
    JOIN gestion g ON ge.id_gestion = g.id_gestion
    WHERE ge.id_gestion = p_id_gestion;
END

CREATE PROCEDURE `GetUsuarioPorGestionID` (IN `p_id_gestion` INT, IN `p_id_person` INT)   BEGIN
    -- Ejecutar la consulta para obtener los detalles del usuario asociado a una gestión específica y sus empresas
    SELECT 
        u.nombre_usuario AS nombre_usuario, 
        e.nombre AS nombre_empresa, 
        p.email AS email_persona, 
        g.id_person
    FROM gestionempresas ge
    JOIN empresa e ON ge.id_empresa = e.id_empresa
    JOIN usuarioempresa g ON e.id_empresa = g.id_empresa
    JOIN usuario u ON g.id_person = u.id_person
    JOIN persona p ON u.id_person = p.id_person
    WHERE ge.id_gestion = p_id_gestion 
      AND g.id_person = p_id_person;
END

CREATE PROCEDURE `GetUsuarioPorGestionNombre` (IN `p_id_gestion` INT, IN `p_nombre_usuario` VARCHAR(45))   BEGIN
    -- Ejecutar la consulta para obtener los detalles del usuario asociado a una gestión específica y con el nombre de usuario dado
    SELECT 
        u.nombre_usuario AS nombre_usuario, 
        e.nombre AS nombre_empresa, 
        p.email AS email_persona, 
        g.id_person
    FROM gestionempresas ge
    JOIN empresa e ON ge.id_empresa = e.id_empresa
    JOIN usuarioempresa g ON e.id_empresa = g.id_empresa
    JOIN usuario u ON g.id_person = u.id_person
    JOIN persona p ON u.id_person = p.id_person
    WHERE ge.id_gestion = p_id_gestion 
      AND u.nombre_usuario = p_nombre_usuario;
END

CREATE PROCEDURE `GetUsuariosPorGestion` (IN `p_id_gestion` INT)   BEGIN
    -- Ejecutar la consulta para obtener los usuarios asociados a las empresas gestionadas en una gestión específica
    SELECT 
        u.nombre_usuario, 
        e.nombre AS nombre_empresa, 
        p.email, 
        p.nombre AS nombre_persona,
        p.id_person AS id
    FROM gestionempresas ge
    JOIN empresa e ON ge.id_empresa = e.id_empresa
    JOIN usuarioempresa ue ON e.id_empresa = ue.id_empresa
    JOIN usuario u ON ue.id_person = u.id_person
    JOIN persona p ON u.id_person = p.id_person
    WHERE ge.id_gestion = p_id_gestion;
END

CREATE PROCEDURE `GetUsuariosPorGestionEmpresa` (IN `p_id_gestion` INT, IN `p_nombre_empresa` VARCHAR(100))   BEGIN
    -- Ejecutar la consulta para obtener los detalles del usuario asociado a una gestión específica y a una empresa con el nombre dado
    SELECT 
        u.nombre_usuario AS nombre_usuario, 
        e.nombre AS nombre_empresa, 
        p.email AS email_persona, 
        g.id_person
    FROM gestionempresas ge
    JOIN empresa e ON ge.id_empresa = e.id_empresa
    JOIN usuarioempresa g ON e.id_empresa = g.id_empresa
    JOIN usuario u ON g.id_person = u.id_person
    JOIN persona p ON u.id_person = p.id_person
    WHERE ge.id_gestion = p_id_gestion 
      AND e.nombre = p_nombre_empresa;
END

CREATE PROCEDURE `InsertGestionEmpresas` (IN `p_nombre_empresa` VARCHAR(100), IN `p_id_gestion` INT, IN `p_id_person` INT)   BEGIN
    DECLARE empresa_count INT;
    DECLARE empresa_id INT;
    DECLARE debug_message VARCHAR(255);

    -- Verificar si la empresa existe en la tabla `empresa`
    SELECT COUNT(*) INTO empresa_count
    FROM empresa p JOIN gestorEmpresas g
    ON p.nombre = g.nombre
    WHERE p.nombre = p_nombre_empresa AND g.id_person = p_id_person;

    -- Depurar el valor de empresa_count
    SET debug_message = CONCAT('empresa_count = ', empresa_count);
    SELECT debug_message;

    IF empresa_count = 0 THEN
        -- Insertar en `gestorEmpresas` y obtener el id_empresa recién generado
        INSERT INTO gestorEmpresas (id_person, nombre)
        VALUES (p_id_person, p_nombre_empresa);
        
        -- Obtener el id_empresa recién insertado
        SELECT id_empresa INTO empresa_id
        FROM gestorEmpresas
        WHERE id_person = p_id_person AND nombre = p_nombre_empresa;
        
        -- Depurar el valor de empresa_id
        SET debug_message = CONCAT('empresa_id = ', empresa_id);
        SELECT debug_message;

        -- Insertar en la tabla `empresa`
        INSERT INTO empresa (id_empresa, nombre, capacidad, gestionada)
        VALUES (empresa_id, p_nombre_empresa, 100, 0);
        
        -- Insertar en la tabla `gestionempresas`
        INSERT INTO gestionempresas (id_empresa, id_gestion)
        VALUES (empresa_id, p_id_gestion);
    ELSE
        -- Lanzar un error si la empresa ya está asociada a otra gestión
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La empresa ya está asociada a otra gestión.';
    END IF;
END

CREATE PROCEDURE `RemoveUsuarioDeEmpresa` (IN `p_id_person` INT, IN `p_id_empresa` INT)   BEGIN
    DECLARE v_empresa_count INT;

    -- Iniciar transacción
    START TRANSACTION;

    -- Eliminar la relación entre el usuario y la empresa en la tabla `usuarioempresa`
    DELETE FROM usuarioempresa
    WHERE id_person = p_id_person
      AND id_empresa = p_id_empresa;

    -- Contar el número de empresas a las que el usuario sigue asociado
    SELECT COUNT(*) INTO v_empresa_count
    FROM usuarioempresa
    WHERE id_person = p_id_person;

    -- Si el usuario no está asociado a ninguna otra empresa, eliminar al usuario
    IF v_empresa_count = 0 THEN
        DELETE FROM usuario
        WHERE id_person = p_id_person;
        
        -- Opcional: También eliminar al usuario de la tabla `persona` si es necesario
        DELETE FROM persona
        WHERE id_person = p_id_person;
    END IF;

    -- Confirmar la transacción
    COMMIT;
END

CREATE PROCEDURE `UpdateGestion` (IN `p_id_gestion` INT, IN `p_nombre_gestion` VARCHAR(255), IN `p_descripcion` TEXT, IN `p_gestor_activo` INT)   BEGIN
    -- Verificar si el gestor activo tiene permisos sobre la gestión
    IF NOT EXISTS (
        SELECT 1 
        FROM gestionar 
        WHERE id_gestion = p_id_gestion AND id_person = p_gestor_activo
    ) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No tienes permiso para actualizar esta gestión. No eres el gestor asignado.';
    ELSE
        -- Realizar la actualización de la gestión
        UPDATE gestion
        SET nombre_gestion = p_nombre_gestion,
            descripcion = p_descripcion
        WHERE id_gestion = p_id_gestion;
    END IF;
END

CREATE PROCEDURE `ValidarLoginGestor` (IN `p_email` VARCHAR(100), IN `p_password` VARCHAR(100), IN `p_ip_address` VARCHAR(45))   BEGIN
    DECLARE v_id_person INT;
    DECLARE v_password VARCHAR(100);

    -- Comprobar si existe un gestor con el email proporcionado
    SELECT g.id_person, g.password
    INTO v_id_person, v_password
    FROM gestor g
    JOIN persona p ON g.id_person = p.id_person
    WHERE p.email = p_email;

    -- Si no se encuentra el email, devolver un error
    IF v_id_person IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El email proporcionado no existe.';
    ELSE
        -- Comprobar si el password coincide
        IF v_password = p_password THEN
            -- El password es correcto, registrar el inicio de sesión en logins
            INSERT INTO logins (id_person, login_time, ip_address)
            VALUES (v_id_person, NOW(), p_ip_address);
            
            -- Devolver éxito
            SELECT 'Inicio de sesión exitoso' AS resultado;
            SELECT v_id_person AS id_inicio;
        ELSE
            -- El password es incorrecto
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Password incorrecto.';
        END IF;
    END IF;
END

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresa`
--

CREATE TABLE `empresa` (
  `id_empresa` int NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `capacidad` int DEFAULT NULL,
  `gestionada` tinyint(1) DEFAULT NULL
);


--
-- Estructura de tabla para la tabla `gestion`
--

CREATE TABLE `gestion` (
  `id_gestion` int NOT NULL,
  `descripcion` text,
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `nombre_gestion` varchar(45) NOT NULL,
  `id_person` int DEFAULT NULL
);


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionar`
--

CREATE TABLE `gestionar` (
  `id_person` int NOT NULL,
  `id_gestion` int NOT NULL
);


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestionempresas`
--

CREATE TABLE `gestionempresas` (
  `id_empresa` int NOT NULL,
  `id_gestion` int NOT NULL
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestor`
--

CREATE TABLE `gestor` (
  `id_person` int NOT NULL,
  `password` varchar(100) NOT NULL
);


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestorEmpresas`
--

CREATE TABLE `gestorEmpresas` (
  `id_person` int NOT NULL,
  `id_empresa` int NOT NULL,
  `nombre` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `logins`
--

CREATE TABLE `logins` (
  `id_login` int NOT NULL,
  `id_person` int DEFAULT NULL,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) DEFAULT NULL
);



-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `nombre` varchar(50) NOT NULL,
  `apellidos` varchar(50) NOT NULL,
  `dni` varchar(50) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `id_person` int NOT NULL
);



-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `fecha_creación` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_person` int NOT NULL,
  `nombre_usuario` varchar(45) NOT NULL
);


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarioempresa`
--

CREATE TABLE `usuarioempresa` (
  `id_person` int NOT NULL,
  `id_empresa` int NOT NULL,
  `id_usuario_empresa` int NOT NULL
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_login_details`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_login_details` (
`id_login` int
,`nombre_persona` varchar(50)
,`email` varchar(100)
,`login_time` datetime
,`ip_address` varchar(45)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `v_login_details`
--
DROP TABLE IF EXISTS `v_login_details`;

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_login_details`  AS SELECT `l`.`id_login` AS `id_login`, `p`.`nombre` AS `nombre_persona`, `p`.`email` AS `email`, `l`.`login_time` AS `login_time`, `l`.`ip_address` AS `ip_address` FROM (`logins` `l` join `persona` `p` on((`l`.`id_person` = `p`.`id_person`))) ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `empresa`
--
ALTER TABLE `empresa`
  ADD PRIMARY KEY (`id_empresa`);

--
-- Indices de la tabla `gestion`
--
ALTER TABLE `gestion`
  ADD PRIMARY KEY (`id_gestion`);

--
-- Indices de la tabla `gestionar`
--
ALTER TABLE `gestionar`
  ADD PRIMARY KEY (`id_gestion`,`id_person`),
  ADD KEY `gestionar_ibfk_1` (`id_person`);

--
-- Indices de la tabla `gestionempresas`
--
ALTER TABLE `gestionempresas`
  ADD PRIMARY KEY (`id_empresa`,`id_gestion`);

--
-- Indices de la tabla `gestor`
--
ALTER TABLE `gestor`
  ADD PRIMARY KEY (`id_person`);

--
-- Indices de la tabla `gestorEmpresas`
--
ALTER TABLE `gestorEmpresas`
  ADD UNIQUE KEY `id_empresa` (`id_empresa`);

--
-- Indices de la tabla `logins`
--
ALTER TABLE `logins`
  ADD PRIMARY KEY (`id_login`),
  ADD KEY `id_person` (`id_person`);

--
-- Indices de la tabla `persona`
--
ALTER TABLE `persona`
  ADD PRIMARY KEY (`id_person`),
  ADD UNIQUE KEY `unique_email` (`email`),
  ADD UNIQUE KEY `unique_dni` (`dni`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_person`),
  ADD UNIQUE KEY `id_person` (`id_person`),
  ADD UNIQUE KEY `nombre_usuario_UNIQUE` (`nombre_usuario`);

--
-- Indices de la tabla `usuarioempresa`
--
ALTER TABLE `usuarioempresa`
  ADD PRIMARY KEY (`id_person`,`id_empresa`),
  ADD UNIQUE KEY `id_usuario_empresa_UNIQUE` (`id_usuario_empresa`),
  ADD KEY `id_empresa` (`id_empresa`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `empresa`
--
ALTER TABLE `empresa`
  MODIFY `id_empresa` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;

--
-- AUTO_INCREMENT de la tabla `gestion`
--
ALTER TABLE `gestion`
  MODIFY `id_gestion` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=94;

--
-- AUTO_INCREMENT de la tabla `gestorEmpresas`
--
ALTER TABLE `gestorEmpresas`
  MODIFY `id_empresa` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;

--
-- AUTO_INCREMENT de la tabla `logins`
--
ALTER TABLE `logins`
  MODIFY `id_login` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=124;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_person` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=71;

--
-- AUTO_INCREMENT de la tabla `usuarioempresa`
--
ALTER TABLE `usuarioempresa`
  MODIFY `id_usuario_empresa` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `gestionar`
--
ALTER TABLE `gestionar`
  ADD CONSTRAINT `gestionar_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `gestor` (`id_person`),
  ADD CONSTRAINT `gestionar_ibfk_2` FOREIGN KEY (`id_gestion`) REFERENCES `gestion` (`id_gestion`);

--
-- Filtros para la tabla `gestionempresas`
--
ALTER TABLE `gestionempresas`
  ADD CONSTRAINT `gestion_ibk2_2` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`);

--
-- Filtros para la tabla `gestor`
--
ALTER TABLE `gestor`
  ADD CONSTRAINT `gestor_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `persona` (`id_person`);

--
-- Filtros para la tabla `logins`
--
ALTER TABLE `logins`
  ADD CONSTRAINT `logins_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `persona` (`id_person`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `persona` (`id_person`);

--
-- Filtros para la tabla `usuarioempresa`
--
ALTER TABLE `usuarioempresa`
  ADD CONSTRAINT `usuarioempresa_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `usuario` (`id_person`),
  ADD CONSTRAINT `usuarioempresa_ibfk_2` FOREIGN KEY (`id_empresa`) REFERENCES `empresa` (`id_empresa`);
COMMIT;

