package v1

import (
	"net/http"

	"github.com/MINIOpenSource/CIMS-backend/internal/model"
	"github.com/MINIOpenSource/CIMS-backend/internal/service"
	"github.com/gin-gonic/gin"
)

type ClientHandler struct {
	configService *service.ConfigService
	clientService *service.ClientService
}

func NewClientHandler() *ClientHandler {
	return &ClientHandler{
		configService: service.NewConfigService(),
		clientService: service.NewClientService(),
	}
}

func (h *ClientHandler) RegisterRoutes(r *gin.RouterGroup) {
	clientGroup := r.Group("/client")
	{
		clientGroup.GET("/:client_uid/manifest", h.GetManifest)
		clientGroup.GET("/:resource_type", h.GetResource)
	}
}

func (h *ClientHandler) GetManifest(c *gin.Context) {
	clientUID := c.Param("client_uid")

	profile, err := h.configService.GetClientProfile(clientUID)
	if err != nil {
		// Defaults
		profile = &model.ClientProfile{
			ClassPlan:       "default_classplan",
			TimeLayout:      "default_timelayout",
			Subjects:        "default_subjects",
			DefaultSettings: "default_settings",
			Policy:          "default_policy",
		}
	}

	buildSource := func(rType, name string) map[string]interface{} {
		// Query version
		ver := int64(0)
		switch rType {
		case "ClassPlan":
			if f, err := h.configService.GetClassPlanFile(name); err == nil { ver = f.Version }
		case "TimeLayout":
			if f, err := h.configService.GetTimeLayoutFile(name); err == nil { ver = f.Version }
		case "Subjects":
			if f, err := h.configService.GetSubjectFile(name); err == nil { ver = f.Version }
		case "DefaultSettings":
			if f, err := h.configService.GetSettingsFile(name); err == nil { ver = f.Version }
		case "Policy":
			if f, err := h.configService.GetPolicyFile(name); err == nil { ver = f.Version }
		}

		return map[string]interface{}{
			"Value":   "/api/v1/client/" + rType + "?name=" + name,
			"Version": ver,
		}
	}

	response := map[string]interface{}{
		"ClassPlanSource":       buildSource("ClassPlan", profile.ClassPlan),
		"TimeLayoutSource":      buildSource("TimeLayout", profile.TimeLayout),
		"SubjectsSource":        buildSource("Subjects", profile.Subjects),
		"DefaultSettingsSource": buildSource("DefaultSettings", profile.DefaultSettings),
		"PolicySource":          buildSource("Policy", profile.Policy),
		"ServerKind":            1,
		"OrganizationName":      "ClassIsland Server",
	}

	c.JSON(http.StatusOK, response)
}

func (h *ClientHandler) GetResource(c *gin.Context) {
	resourceType := c.Param("resource_type")
	name := c.Query("name")

	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "name is required"})
		return
	}

	var content string
	var err error

	switch resourceType {
	case "ClassPlan":
		var f *model.CPFile
		f, err = h.configService.GetClassPlanFile(name)
		if err == nil { content = f.Content }
	case "TimeLayout":
		var f *model.TLFile
		f, err = h.configService.GetTimeLayoutFile(name)
		if err == nil { content = f.Content }
	case "Subjects":
		var f *model.SubFile
		f, err = h.configService.GetSubjectFile(name)
		if err == nil { content = f.Content }
	case "DefaultSettings":
		var f *model.SettingsFile
		f, err = h.configService.GetSettingsFile(name)
		if err == nil { content = f.Content }
	case "Policy":
		var f *model.PolicyFile
		f, err = h.configService.GetPolicyFile(name)
		if err == nil { content = f.Content }
	default:
		c.JSON(http.StatusNotFound, gin.H{"error": "Unknown resource type"})
		return
	}

	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Resource not found"})
		return
	}

	c.Header("Content-Type", "application/json")
	c.String(http.StatusOK, content)
}
