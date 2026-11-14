(function () {
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function setActiveWeaponUi(weaponKey) {
        document.querySelectorAll('[data-weapon-tab]').forEach(function (button) {
            button.classList.toggle('active', button.dataset.weaponTab === weaponKey);
        });

        document.querySelectorAll('[data-weapon-panel]').forEach(function (panel) {
            panel.classList.toggle('active', panel.dataset.weaponPanel === weaponKey);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var dataTag = document.getElementById('simulator-data');
        var defaultTag = document.getElementById('default-weapon');
        var canvas = document.getElementById('weapon-canvas');
        var stage = document.getElementById('simulator-stage');
        var fallback = document.getElementById('simulator-fallback');

        if (!dataTag || !defaultTag || !canvas || !stage) {
            return;
        }

        var weaponData = JSON.parse(dataTag.textContent);
        var defaultWeapon = JSON.parse(defaultTag.textContent);
        var guidePanels = {};
        document.querySelectorAll('[data-weapon-panel]').forEach(function (panel) {
            guidePanels[panel.dataset.weaponPanel] = panel;
        });

        if (!window.THREE) {
            if (fallback) {
                fallback.classList.add('show');
            }
            return;
        }

        var renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            antialias: true,
            alpha: true
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        if (THREE.sRGBEncoding) {
            renderer.outputEncoding = THREE.sRGBEncoding;
        } else if (THREE.SRGBColorSpace) {
            renderer.outputColorSpace = THREE.SRGBColorSpace;
        }
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        if (THREE.ACESFilmicToneMapping) {
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.12;
        }
        if ('useLegacyLights' in renderer) {
            renderer.useLegacyLights = false;
        } else if ('physicallyCorrectLights' in renderer) {
            renderer.physicallyCorrectLights = true;
        }

        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);

        scene.add(new THREE.HemisphereLight(0xffffff, 0x25384d, 1.1));

        var mainLight = new THREE.DirectionalLight(0xffffff, 1.7);
        mainLight.position.set(7, 9, 8);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 1024;
        mainLight.shadow.mapSize.height = 1024;
        scene.add(mainLight);

        var fillLight = new THREE.DirectionalLight(0x8bbcff, 0.62);
        fillLight.position.set(-6, 3, -4);
        scene.add(fillLight);

        var rimLight = new THREE.DirectionalLight(0xfff1d6, 0.75);
        rimLight.position.set(-5, 6, 7);
        scene.add(rimLight);

        var grid = new THREE.GridHelper(26, 26, 0x5f819d, 0x2c445b);
        grid.position.y = -5.2;
        scene.add(grid);

        var floor = new THREE.Mesh(
            new THREE.CircleGeometry(7.5, 48),
            new THREE.MeshPhongMaterial({
                color: 0x8cb1cf,
                transparent: true,
                opacity: 0.18
            })
        );
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -5.1;
        floor.receiveShadow = true;
        scene.add(floor);

        var group = new THREE.Group();
        scene.add(group);

        var state = {
            weaponKey: defaultWeapon,
            parts: [],
            drag: false,
            lastX: 0,
            lastY: 0,
            rotX: -0.18,
            rotY: 0.55,
            rotZ: 0,
            targetRotX: -0.18,
            targetRotY: 0.55,
            targetRotZ: 0,
            zoom: 1,
            targetZoom: 1,
            cameraBase: new THREE.Vector3(),
            targetCamera: new THREE.Vector3(),
            autoRotate: true
        };

        var textureLoader = new THREE.TextureLoader();
        var fbxLoader = window.THREE.FBXLoader ? new THREE.FBXLoader() : null;
        var loadToken = 0;
        var minZoom = 0.45;
        var maxZoom = 1.75;
        var zoomStep = 0.12;

        function resizeScene() {
            var width = stage.clientWidth;
            var height = stage.clientHeight;
            renderer.setSize(width, height, false);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
        }

        function createGeometry(definition) {
            if (definition.shape === 'cylinder') {
                return new THREE.CylinderGeometry(
                    definition.size[0],
                    definition.size[1],
                    definition.size[2],
                    definition.size[3] || 20
                );
            }

            return new THREE.BoxGeometry(
                definition.size[0],
                definition.size[1],
                definition.size[2]
            );
        }

        function disposeObject(object) {
            var disposedMaterials = [];
            var disposedTextures = [];

            object.traverse(function (child) {
                if (child.geometry) {
                    child.geometry.dispose();
                }

                if (child.material) {
                    var materials = Array.isArray(child.material) ? child.material : [child.material];
                    materials.forEach(function (material) {
                        if (disposedMaterials.indexOf(material) !== -1) {
                            return;
                        }

                        Object.keys(material).forEach(function (key) {
                            var value = material[key];
                            if (value && value.isTexture && disposedTextures.indexOf(value) === -1) {
                                disposedTextures.push(value);
                                value.dispose();
                            }
                        });
                        disposedMaterials.push(material);
                        material.dispose();
                    });
                }
            });
        }

        function clearGroup() {
            while (group.children.length) {
                var child = group.children.pop();
                disposeObject(child);
            }
            state.parts = [];
        }

        function updateWeaponText() {
            var panel = guidePanels[state.weaponKey];
            var currentWeaponLabel = document.getElementById('current-weapon-label');
            var currentViewLabel = document.getElementById('current-view-label');

            if (panel) {
                var heading = panel.querySelector('.panel_title');
                if (heading && currentWeaponLabel) {
                    currentWeaponLabel.textContent = heading.textContent;
                }
            }

            if (currentViewLabel) {
                currentViewLabel.textContent = '3D model gorunusi';
            }
        }

        function updateTargets() {
            state.parts.forEach(function (part) {
                var targetPos = part.definition.assembled_pos;
                var targetRot = part.definition.assembled_rot;

                part.targetPosition.set(targetPos[0], targetPos[1], targetPos[2]);
                part.targetRotation.set(targetRot[0], targetRot[1], targetRot[2]);
            });

            updateWeaponText();
        }

        function updateCameraTarget(immediate) {
            state.targetCamera.copy(state.cameraBase).multiplyScalar(state.targetZoom);
            if (immediate) {
                state.zoom = state.targetZoom;
                camera.position.copy(state.targetCamera);
                camera.lookAt(0, 0, 0);
            }
        }

        function zoomBy(amount) {
            state.targetZoom = clamp(state.targetZoom + amount, minZoom, maxZoom);
            updateCameraTarget(false);
        }

        function resetView() {
            var config = weaponData[state.weaponKey] || {};
            var view = config.view || {};
            state.targetRotX = typeof view.rotX === 'number' ? view.rotX : -0.18;
            state.targetRotY = typeof view.rotY === 'number' ? view.rotY : 0.55;
            state.targetRotZ = typeof view.rotZ === 'number' ? view.rotZ : 0;
            state.targetZoom = 1;
            updateCameraTarget(false);
        }

        function firstDefined(primary, fallback, defaultValue) {
            if (typeof primary !== 'undefined') {
                return primary;
            }

            if (typeof fallback !== 'undefined') {
                return fallback;
            }

            return defaultValue;
        }

        function loadTexture(url, isColorTexture, flipY) {
            if (!url) {
                return null;
            }

            var texture = textureLoader.load(url);
            texture.flipY = typeof flipY === 'boolean' ? flipY : true;
            if (renderer.capabilities && renderer.capabilities.getMaxAnisotropy) {
                texture.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
            }
            if (isColorTexture) {
                if (THREE.sRGBEncoding) {
                    texture.encoding = THREE.sRGBEncoding;
                } else if (THREE.SRGBColorSpace) {
                    texture.colorSpace = THREE.SRGBColorSpace;
                }
            }
            texture.needsUpdate = true;
            return texture;
        }

        function fitModelToSize(object, targetSize) {
            var box = new THREE.Box3().setFromObject(object);
            var size = new THREE.Vector3();
            var center = new THREE.Vector3();
            box.getSize(size);

            var longestSide = Math.max(size.x, size.y, size.z);
            if (longestSide > 0 && targetSize) {
                var scale = targetSize / longestSide;
                object.scale.setScalar(scale);
            }

            box.setFromObject(object);
            box.getCenter(center);
            object.position.sub(center);
        }

        function getMaterialLabel(child) {
            var labels = [child.name || ''];
            var materials = Array.isArray(child.material) ? child.material : [child.material];

            materials.forEach(function (material) {
                if (material && material.name) {
                    labels.push(material.name);
                }
            });

            return labels.join(' ').toLowerCase();
        }

        function getMaterialChoice(child, modelConfig) {
            var materialConfigs = modelConfig.materials || [];
            var label = getMaterialLabel(child);

            for (var i = 0; i < materialConfigs.length; i += 1) {
                var matchers = materialConfigs[i].match || [];
                for (var j = 0; j < matchers.length; j += 1) {
                    if (label.indexOf(String(matchers[j]).toLowerCase()) !== -1) {
                        return {
                            key: 'material-' + i,
                            config: materialConfigs[i]
                        };
                    }
                }
            }

            return {
                key: 'model',
                config: modelConfig
            };
        }

        function applyModelMaterial(object, modelConfig) {
            var textureCache = {};
            var materialCache = {};

            function configuredValue(materialConfig, key, defaultValue) {
                return firstDefined(materialConfig[key], modelConfig[key], defaultValue);
            }

            function configuredTexture(materialConfig, key, isColorTexture) {
                var url = configuredValue(materialConfig, key, null);
                var flipY = configuredValue(materialConfig, 'flip_y', true);
                var cacheKey = url + '|' + isColorTexture + '|' + flipY;

                if (!url) {
                    return null;
                }

                if (!textureCache[cacheKey]) {
                    textureCache[cacheKey] = loadTexture(url, isColorTexture, flipY);
                }

                return textureCache[cacheKey];
            }

            function createConfiguredMaterial(materialConfig) {
                var normalScale = configuredValue(materialConfig, 'normal_scale', null);
                var material = new THREE.MeshStandardMaterial({
                    color: configuredValue(materialConfig, 'color', 0xffffff),
                    map: configuredTexture(materialConfig, 'texture', true),
                    normalMap: configuredTexture(materialConfig, 'normal', false),
                    roughnessMap: configuredTexture(materialConfig, 'roughness', false),
                    metalnessMap: configuredTexture(materialConfig, 'metalness', false),
                    aoMap: configuredTexture(materialConfig, 'occlusion', false) || configuredTexture(materialConfig, 'ao', false),
                    aoMapIntensity: configuredValue(materialConfig, 'ao_intensity', 0.9),
                    metalness: configuredValue(materialConfig, 'metalness_value', 0.45),
                    roughness: configuredValue(materialConfig, 'roughness_value', 0.56),
                    envMapIntensity: configuredValue(materialConfig, 'env_intensity', 0.65)
                });

                if (normalScale && material.normalScale) {
                    material.normalScale.set(normalScale[0], normalScale[1]);
                }

                return material;
            }

            object.traverse(function (child) {
                if (!child.isMesh) {
                    return;
                }

                var sourceMaterial = Array.isArray(child.material) ? child.material[0] : child.material;
                child.castShadow = true;
                child.receiveShadow = true;
                var choice = getMaterialChoice(child, modelConfig);
                if (!materialCache[choice.key]) {
                    materialCache[choice.key] = createConfiguredMaterial(choice.config);
                }
                if (!materialCache[choice.key].map && sourceMaterial && sourceMaterial.color) {
                    materialCache[choice.key].color.copy(sourceMaterial.color);
                }
                if (materialCache[choice.key].aoMap && child.geometry && child.geometry.attributes.uv && !child.geometry.attributes.uv2) {
                    child.geometry.setAttribute('uv2', child.geometry.attributes.uv);
                }
                child.material = materialCache[choice.key];
            });
        }

        function addModelPart(object, modelConfig) {
            fitModelToSize(object, modelConfig.fit || 10);
            applyModelMaterial(object, modelConfig);

            var assembledPos = modelConfig.assembled_pos || [0, 0, 0];
            var assembledRot = modelConfig.assembled_rot || [0, 0, 0];
            object.position.set(assembledPos[0], assembledPos[1], assembledPos[2]);
            object.rotation.set(assembledRot[0], assembledRot[1], assembledRot[2]);
            group.add(object);

            state.parts.push({
                mesh: object,
                definition: {
                    assembled_pos: assembledPos,
                    assembled_rot: assembledRot
                },
                targetPosition: new THREE.Vector3(assembledPos[0], assembledPos[1], assembledPos[2]),
                targetRotation: new THREE.Euler(assembledRot[0], assembledRot[1], assembledRot[2])
            });
        }

        function loadFallbackParts(config) {
            config.parts.forEach(function (definition) {
                var geometry = createGeometry(definition);
                var material = new THREE.MeshStandardMaterial({
                    color: definition.color,
                    metalness: definition.shape === 'cylinder' ? 0.55 : 0.28,
                    roughness: definition.shape === 'cylinder' ? 0.34 : 0.62
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(definition.assembled_pos[0], definition.assembled_pos[1], definition.assembled_pos[2]);
                mesh.rotation.set(definition.assembled_rot[0], definition.assembled_rot[1], definition.assembled_rot[2]);
                group.add(mesh);

                state.parts.push({
                    mesh: mesh,
                    definition: definition,
                    targetPosition: new THREE.Vector3(definition.assembled_pos[0], definition.assembled_pos[1], definition.assembled_pos[2]),
                    targetRotation: new THREE.Euler(definition.assembled_rot[0], definition.assembled_rot[1], definition.assembled_rot[2])
                });
            });
        }

        function loadWeapon(weaponKey) {
            var config = weaponData[weaponKey];
            if (!config) {
                return;
            }

            loadToken += 1;
            var currentToken = loadToken;
            state.weaponKey = weaponKey;
            var view = config.view || {};
            state.targetRotX = typeof view.rotX === 'number' ? view.rotX : -0.18;
            state.targetRotY = typeof view.rotY === 'number' ? view.rotY : 0.55;
            state.targetRotZ = typeof view.rotZ === 'number' ? view.rotZ : 0;
            state.targetZoom = 1;
            state.autoRotate = typeof view.autoRotate === 'boolean' ? view.autoRotate : true;
            clearGroup();

            if (config.model && fbxLoader) {
                var placeholder = new THREE.Mesh(
                    new THREE.BoxGeometry(8.8, 0.5, 0.8),
                    new THREE.MeshStandardMaterial({
                        color: 0x6d7f68,
                        metalness: 0.35,
                        roughness: 0.7,
                        transparent: true,
                        opacity: 0.45
                    })
                );
                group.add(placeholder);

                fbxLoader.load(config.model.url, function (object) {
                    if (currentToken !== loadToken) {
                        disposeObject(object);
                        return;
                    }

                    clearGroup();
                    addModelPart(object, config.model);
                    updateTargets();
                }, undefined, function () {
                    if (currentToken !== loadToken) {
                        return;
                    }

                    clearGroup();
                    loadFallbackParts(config);
                    updateTargets();
                });
            } else {
                loadFallbackParts(config);
            }

            state.cameraBase.set(config.camera[0], config.camera[1], config.camera[2]);
            updateCameraTarget(true);
            setActiveWeaponUi(weaponKey);
            updateTargets();
        }

        function animate() {
            requestAnimationFrame(animate);

            state.rotX += (state.targetRotX - state.rotX) * 0.08;
            state.rotY += (state.targetRotY - state.rotY) * 0.08;
            state.rotZ += (state.targetRotZ - state.rotZ) * 0.08;
            group.rotation.x = state.rotX;
            group.rotation.y = state.rotY;
            group.rotation.z = state.rotZ;
            state.zoom += (state.targetZoom - state.zoom) * 0.12;
            state.targetCamera.copy(state.cameraBase).multiplyScalar(state.zoom);
            camera.position.lerp(state.targetCamera, 0.22);
            camera.lookAt(0, 0, 0);

            if (!state.drag && state.autoRotate) {
                state.targetRotY += 0.0022;
            }

            state.parts.forEach(function (part) {
                part.mesh.position.lerp(part.targetPosition, 0.1);
                part.mesh.rotation.x += (part.targetRotation.x - part.mesh.rotation.x) * 0.1;
                part.mesh.rotation.y += (part.targetRotation.y - part.mesh.rotation.y) * 0.1;
                part.mesh.rotation.z += (part.targetRotation.z - part.mesh.rotation.z) * 0.1;
            });

            renderer.render(scene, camera);
        }

        document.querySelectorAll('[data-weapon-tab]').forEach(function (button) {
            button.addEventListener('click', function () {
                loadWeapon(button.dataset.weaponTab);
            });
        });

        function bindButton(id, handler) {
            var button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            }
        }

        bindButton('zoom-in', function () {
            zoomBy(-zoomStep);
        });

        bindButton('zoom-out', function () {
            zoomBy(zoomStep);
        });

        bindButton('reset-view', resetView);

        canvas.addEventListener('pointerdown', function (event) {
            state.drag = true;
            state.lastX = event.clientX;
            state.lastY = event.clientY;
        });

        window.addEventListener('pointerup', function () {
            state.drag = false;
        });

        window.addEventListener('pointermove', function (event) {
            if (!state.drag) {
                return;
            }

            var diffX = event.clientX - state.lastX;
            var diffY = event.clientY - state.lastY;
            state.lastX = event.clientX;
            state.lastY = event.clientY;

            state.targetRotY += diffX * 0.01;
            state.targetRotX = clamp(state.targetRotX + diffY * 0.006, -1.0, 0.6);
        });

        canvas.addEventListener('wheel', function (event) {
            event.preventDefault();
            zoomBy(event.deltaY > 0 ? zoomStep : -zoomStep);
        }, { passive: false });

        window.addEventListener('resize', resizeScene);

        resizeScene();
        loadWeapon(defaultWeapon);
        animate();
    });
})();
