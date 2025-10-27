import bpy
import requests
import tempfile
import traceback
import os
import shutil
from contextlib import suppress

# Constants defined locally to avoid circular imports
RODIN_FREE_TRIAL_KEY = "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"

class Hyper3DHandlers:
    """Handlers for Hyper3D Rodin integration"""

    def create_rodin_job(self, text_prompt=None, images=None, bbox_condition=None):
        """Create a new Hyper3D Rodin generation job"""
        try:
            # Determine the mode based on API key
            api_key = bpy.context.scene.blendermcp_hyper3d_api_key
            mode = bpy.context.scene.blendermcp_hyper3d_mode

            if mode == "MAIN_SITE":
                # Use the main site API
                url = "https://hyperhuman.deemos.com/api/v2/generate"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }

                # Prepare the payload
                payload = {
                    "text": text_prompt,
                    "bbox_condition": bbox_condition,
                }

                if images:
                    # For images, we need to handle them differently
                    # This is a simplified version - the full implementation would handle image uploads
                    payload["images"] = images

                response = requests.post(url, headers=headers, json=payload)

            elif mode == "FAL_AI":
                # Use FAL AI API
                url = "https://queue.fal.run/fal-ai/hyper3d/"
                headers = {
                    "Authorization": f"Key {api_key}",
                    "Content-Type": "application/json"
                }

                # Prepare the payload for FAL AI
                payload = {
                    "text_prompt": text_prompt,
                    "bbox_condition": bbox_condition,
                }

                if images:
                    payload["input_image_url"] = images[0] if isinstance(images, list) else images

                response = requests.post(url, headers=headers, json=payload)
            else:
                return {"error": f"Unknown Hyper3D mode: {mode}"}

            if response.status_code == 200:
                data = response.json()

                if mode == "MAIN_SITE":
                    # Extract job information
                    job_id = data.get("job_id")
                    if not job_id:
                        return {"error": "No job_id returned from Hyper3D API"}

                    return {
                        "uuid": job_id,
                        "jobs": {
                            "subscription_key": job_id,  # For MAIN_SITE, use job_id as subscription_key
                        },
                        "submit_time": True
                    }

                elif mode == "FAL_AI":
                    # Extract request ID for FAL AI
                    request_id = data.get("request_id")
                    if not request_id:
                        return {"error": "No request_id returned from FAL AI"}

                    return {
                        "uuid": request_id,  # Use request_id as uuid for consistency
                        "jobs": {
                            "subscription_key": request_id,  # For FAL_AI, use request_id as subscription_key
                        },
                        "submit_time": True
                    }
            else:
                return {"error": f"API request failed with status code {response.status_code}: {response.text}"}

        except Exception as e:
            return {"error": f"Failed to create Rodin job: {str(e)}"}

    def poll_rodin_job_status(self, subscription_key=None, request_id=None):
        """Poll the status of a Hyper3D Rodin job"""
        try:
            mode = bpy.context.scene.blendermcp_hyper3d_mode
            api_key = bpy.context.scene.blendermcp_hyper3d_api_key

            if mode == "MAIN_SITE":
                if not subscription_key:
                    return {"error": "subscription_key is required for MAIN_SITE mode"}

                url = f"https://hyperhuman.deemos.com/api/v2/jobs/{subscription_key}"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")

                    # Return status information
                    return {
                        "status": status,
                        "progress": data.get("progress", 0),
                        "message": data.get("message", ""),
                        "data": data
                    }
                else:
                    return {"error": f"Failed to get job status: {response.status_code}"}

            elif mode == "FAL_AI":
                if not request_id:
                    return {"error": "request_id is required for FAL_AI mode"}

                url = f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}"
                headers = {
                    "Authorization": f"Key {api_key}",
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")

                    # Return status information
                    return {
                        "status": status,
                        "message": data.get("message", ""),
                        "data": data
                    }
                else:
                    return {"error": f"Failed to get request status: {response.status_code}"}
            else:
                return {"error": f"Unknown Hyper3D mode: {mode}"}

        except Exception as e:
            return {"error": f"Failed to poll job status: {str(e)}"}

    def _clean_imported_glb(self, filepath, mesh_name=None):
        """Clean up imported GLB/GLTF and return the mesh object"""
        # Get all objects before import
        existing_objects = set(bpy.data.objects)

        # Import the GLB/GLTF file
        if filepath.endswith('.glb'):
            bpy.ops.import_scene.gltf(filepath=filepath)
        elif filepath.endswith('.gltf'):
            bpy.ops.import_scene.gltf(filepath=filepath)
        else:
            raise ValueError("Unsupported file format")

        # Ensure the context is updated
        bpy.context.view_layer.update()

        # Get all imported objects
        imported_objects = list(set(bpy.data.objects) - existing_objects)
        # imported_objects = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]

        if not imported_objects:
            print("Error: No objects were imported.")
            return

        # Identify the mesh object
        mesh_obj = None

        if len(imported_objects) == 1 and imported_objects[0].type == 'MESH':
            mesh_obj = imported_objects[0]
            print("Single mesh imported, no cleanup needed.")
        else:
            if len(imported_objects) == 2:
                empty_objs = [i for i in imported_objects if i.type == "EMPTY"]
                if len(empty_objs) != 1:
                    print("Error: Expected an empty node with one mesh child or a single mesh object.")
                    return
                parent_obj = empty_objs.pop()
                if len(parent_obj.children) == 1:
                    potential_mesh = parent_obj.children[0]
                    if potential_mesh.type == 'MESH':
                        print("GLB structure confirmed: Empty node with one mesh child.")

                        # Unparent the mesh from the empty node
                        potential_mesh.parent = None

                        # Remove the empty node
                        bpy.data.objects.remove(parent_obj)
                        print("Removed empty node, keeping only the mesh.")

                        mesh_obj = potential_mesh
                    else:
                        print("Error: Child is not a mesh object.")
                        return
                else:
                    print("Error: Expected an empty node with one mesh child or a single mesh object.")
                    return
            else:
                print("Error: Expected an empty node with one mesh child or a single mesh object.")
                return

        # Rename the mesh if needed
        try:
            if mesh_obj and mesh_obj.name is not None and mesh_name:
                mesh_obj.name = mesh_name or "ImportedMesh"
                if mesh_obj.data.name is not None:
                    mesh_obj.data.name = mesh_name or "ImportedMesh"
                print(f"Mesh renamed to: {mesh_name or 'ImportedMesh'}")
        except Exception as e:
            print("Having issue with renaming, give up renaming.")

        return mesh_obj

    def import_generated_asset(self, *args, **kwargs):
        match bpy.context.scene.blendermcp_hyper3d_mode:
            case "MAIN_SITE":
                return self.import_generated_asset_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.import_generated_asset_fal_ai(*args, **kwargs)
            case _:
                return f"Error: Unknown Hyper3D Rodin mode!"

    def import_generated_asset_main_site(self, task_uuid: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.post(
            "https://hyperhuman.deemos.com/api/v2/download",
            headers={
                "Authorization": f"Bearer {bpy.context.scene.blendermcp_hyper3d_api_key}",
            },
            json={
                'task_uuid': task_uuid
            }
        )
        data_ = response.json()
        temp_file = None
        for i in data_["list"]:
            if i["name"].endswith(".glb"):
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    prefix=task_uuid,
                    suffix=".glb",
                )

                try:
                    # Download the content
                    response = requests.get(i["url"], stream=True)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Write the content to the temporary file
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)

                    # Close the file
                    temp_file.close()

                except Exception as e:
                    # Clean up the file if there's an error
                    temp_file.close()
                    os.unlink(temp_file.name)
                    return {"succeed": False, "error": str(e)}

                break
        else:
            return {"succeed": False, "error": "Generation failed. Please first make sure that all jobs of the task are done and then try again later."}

        try:
            obj = self._clean_imported_glb(
                filepath=temp_file.name,
                mesh_name=name
            )
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {
                "succeed": True, **result
            }
        except Exception as e:
            return {"succeed": False, "error": str(e)}

    def import_generated_asset_fal_ai(self, request_id: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}",
            headers={
                "Authorization": f"Key {bpy.context.scene.blendermcp_hyper3d_api_key}",
            }
        )
        data_ = response.json()
        temp_file = None

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix=request_id,
            suffix=".glb",
        )

        try:
            # Download the content
            response = requests.get(data_["model_mesh"]["url"], stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Write the content to the temporary file
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

            # Close the file
            temp_file.close()

        except Exception as e:
            # Clean up the file if there's an error
            temp_file.close()
            os.unlink(temp_file.name)
            return {"succeed": False, "error": str(e)}

        try:
            obj = self._clean_imported_glb(
                filepath=temp_file.name,
                mesh_name=name
            )
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {
                "succeed": True, **result
            }
        except Exception as e:
            return {"succeed": False, "error": str(e)}

    @staticmethod
    def _get_aabb(obj):
        """ Returns the world-space axis-aligned bounding box (AABB) of an object. """
        if obj.type != 'MESH':
            raise TypeError("Object must be a mesh")

        # Get the bounding box corners in local space
        local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]

        # Convert to world coordinates
        world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

        # Compute axis-aligned min/max coordinates
        min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
        max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

        return [
            [*min_corner], [*max_corner]
        ]

    def get_hyper3d_status(self):
        """Get the current status of Hyper3D Rodin integration"""
        enabled = bpy.context.scene.blendermcp_use_hyper3d
        api_key = bpy.context.scene.blendermcp_hyper3d_api_key

        if enabled and api_key:
            return {"enabled": True, "message": "Hyper3D Rodin integration is enabled and ready to use."}
        elif enabled and not api_key:
            return {
                "enabled": False,
                "message": """Hyper3D Rodin integration is currently enabled, but API key is not given. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Keep the 'Use Hyper3D Rodin' checkbox checked
                            3. Enter your Hyper3D API Key
                            4. Restart the connection to Claude"""
            }
        else:
            return {
                "enabled": False,
                "message": """Hyper3D Rodin integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Check the 'Use Hyper3D Rodin' checkbox
                            3. Enter your Hyper3D API Key
                            4. Restart the connection to Claude"""
            }