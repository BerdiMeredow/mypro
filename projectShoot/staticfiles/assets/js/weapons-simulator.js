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

        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);

        scene.add(new THREE.HemisphereLight(0xffffff, 0x25384d, 1.25));

        var mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
        mainLight.position.set(7, 9, 8);
        scene.add(mainLight);

        var fillLight = new THREE.DirectionalLight(0x8bbcff, 0.5);
        fillLight.position.set(-6, 3, -4);
        scene.add(fillLight);

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
        scene.add(floor);

        var group = new THREE.Group();
        scene.add(group);

        var state = {
            weaponKey: defaultWeapon,
            stepIndex: 0,
            maxStep: 0,
            parts: [],
            drag: false,
            lastX: 0,
            lastY: 0,
            rotX: -0.18,
            rotY: 0.55,
            targetRotX: -0.18,
            targetRotY: 0.55
        };

        var textureLoader = new THREE.TextureLoader();
        var fbxLoader = window.THREE.FBXLoader ? new THREE.FBXLoader() : null;
        var loadToken = 0;

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
            object.traverse(function (child) {
                if (child.geometry) {
                    child.geometry.dispose();
                }

                if (child.material) {
                    var materials = Array.isArray(child.material) ? child.material : [child.material];
                    materials.forEach(function (material) {
                        Object.keys(material).forEach(function (key) {
                            var value = material[key];
                            if (value && value.isTexture) {
                                value.dispose();
                            }
                        });
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

        function updateStepText() {
            var panel = guidePanels[state.weaponKey];
            var currentWeaponLabel = document.getElementById('current-weapon-label');
            var currentStepLabel = document.getElementById('current-step-label');
            var stepCounter = document.getElementById('step-counter');

            if (panel) {
                var heading = panel.querySelector('.panel_title');
                if (heading && currentWeaponLabel) {
                    currentWeaponLabel.textContent = heading.textContent;
                }

                panel.querySelectorAll('[data-step-index]').forEach(function (item) {
                    var itemIndex = parseInt(item.dataset.stepIndex, 10);
                    item.classList.toggle('active', itemIndex === state.stepIndex);
                    item.classList.toggle('done', itemIndex < state.stepIndex);
                });
            }

            if (currentStepLabel) {
                if (state.stepIndex === 0) {
                    currentStepLabel.textContent = 'Yagday: ygnalan gorunus';
                } else {
                    var stepItems = panel ? panel.querySelectorAll('[data-step-index]') : [];
                    var activeItem = stepItems[state.stepIndex - 1];
                    currentStepLabel.textContent = activeItem ? activeItem.textContent : 'Adam maglumatlary';
                }
            }

            if (stepCounter) {
                stepCounter.textContent = state.stepIndex + ' / ' + state.maxStep + ' adam';
            }
        }

        function updateTargets() {
            state.parts.forEach(function (part) {
                var open = part.definition.order > 0 && part.definition.order <= state.stepIndex;
                var targetPos = open ? part.definition.exploded_pos : part.definition.assembled_pos;
                var targetRot = open ? part.definition.exploded_rot : part.definition.assembled_rot;

                part.targetPosition.set(targetPos[0], targetPos[1], targetPos[2]);
                part.targetRotation.set(targetRot[0], targetRot[1], targetRot[2]);
            });

            updateStepText();
        }

        function loadTexture(url, isColorTexture) {
            if (!url) {
                return null;
            }

            var texture = textureLoader.load(url);
            texture.flipY = false;
            if (isColorTexture) {
                if (THREE.sRGBEncoding) {
                    texture.encoding = THREE.sRGBEncoding;
                } else if (THREE.SRGBColorSpace) {
                    texture.colorSpace = THREE.SRGBColorSpace;
                }
            }
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

        function applyModelMaterial(object, modelConfig) {
            var map = loadTexture(modelConfig.texture, true);
            var normalMap = loadTexture(modelConfig.normal, false);
            var roughnessMap = loadTexture(modelConfig.roughness, false);
            var metalnessMap = loadTexture(modelConfig.metalness, false);
            var aoMap = loadTexture(modelConfig.occlusion || modelConfig.ao, false);

            object.traverse(function (child) {
                if (!child.isMesh) {
                    return;
                }

                child.castShadow = true;
                child.receiveShadow = true;
                if (aoMap && child.geometry && child.geometry.attributes.uv && !child.geometry.attributes.uv2) {
                    child.geometry.setAttribute('uv2', child.geometry.attributes.uv);
                }
                child.material = new THREE.MeshStandardMaterial({
                    map: map,
                    normalMap: normalMap,
                    roughnessMap: roughnessMap,
                    metalnessMap: metalnessMap,
                    aoMap: aoMap,
                    aoMapIntensity: 0.8,
                    metalness: 0.45,
                    roughness: 0.62
                });
            });
        }

        function addModelPart(object, modelConfig, order) {
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
                    order: order,
                    assembled_pos: assembledPos,
                    assembled_rot: assembledRot,
                    exploded_pos: modelConfig.exploded_pos || assembledPos,
                    exploded_rot: modelConfig.exploded_rot || assembledRot
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
            state.stepIndex = 0;
            state.maxStep = guidePanels[weaponKey] ? guidePanels[weaponKey].querySelectorAll('[data-step-index]').length : 0;
            state.targetRotX = -0.18;
            state.targetRotY = 0.55;
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
                    addModelPart(object, config.model, 1);
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

            camera.position.set(config.camera[0], config.camera[1], config.camera[2]);
            camera.lookAt(0, 0, 0);
            setActiveWeaponUi(weaponKey);
            updateTargets();
        }

        function animate() {
            requestAnimationFrame(animate);

            state.rotX += (state.targetRotX - state.rotX) * 0.08;
            state.rotY += (state.targetRotY - state.rotY) * 0.08;
            group.rotation.x = state.rotX;
            group.rotation.y = state.rotY;

            if (!state.drag) {
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

        document.getElementById('prev-step').addEventListener('click', function () {
            state.stepIndex = Math.max(0, state.stepIndex - 1);
            updateTargets();
        });

        document.getElementById('next-step').addEventListener('click', function () {
            state.stepIndex = Math.min(state.maxStep, state.stepIndex + 1);
            updateTargets();
        });

        document.getElementById('explode-all').addEventListener('click', function () {
            state.stepIndex = state.maxStep;
            updateTargets();
        });

        document.getElementById('assemble-all').addEventListener('click', function () {
            state.stepIndex = 0;
            updateTargets();
        });

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

        window.addEventListener('resize', resizeScene);

        resizeScene();
        loadWeapon(defaultWeapon);
        animate();
    });
})();
